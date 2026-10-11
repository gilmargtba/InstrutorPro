param([switch]$InitializeSigningKey)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$sdkRoot = Join-Path $env:LOCALAPPDATA 'Android\Sdk'
$buildTools = Join-Path $sdkRoot 'build-tools\36.0.0'
$signingDirectory = Join-Path $env:LOCALAPPDATA 'InstrutorProCNH\android-signing'
$keyFile = Join-Path $signingDirectory 'release.p12'
$passwordFile = Join-Path $signingDirectory 'release-password.dpapi'
$releaseDirectory = Join-Path $repoRoot 'releases\android'
$unsignedApk = Join-Path $repoRoot 'frontend\android\app\build\outputs\apk\release\app-release-unsigned.apk'
$alignedApk = Join-Path $releaseDirectory 'InstrutorProCNH-aligned.apk'
$signedApk = Join-Path $releaseDirectory 'InstrutorProCNH-android.apk'
$alias = 'instrutorprocnh_release'

if ((Test-Path $keyFile) -xor (Test-Path $passwordFile)) {
    throw 'A chave e a senha protegida precisam existir juntas. Verifique o backup antes de prosseguir.'
}

if (-not (Test-Path $keyFile)) {
    if (-not $InitializeSigningKey) { throw 'Chave de release ausente. Execute novamente com -InitializeSigningKey.' }
    New-Item -ItemType Directory -Path $signingDirectory -Force | Out-Null
    $randomBytes = New-Object byte[] 48
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($randomBytes)
    $password = [Convert]::ToBase64String($randomBytes)
    [Array]::Clear($randomBytes)
    try {
        $env:INSTRUTORPRO_RELEASE_KEY_PASSWORD = $password
        & keytool -genkeypair -keystore $keyFile -storetype PKCS12 -alias $alias -keyalg RSA -keysize 4096 -sigalg SHA256withRSA -validity 10000 -dname 'CN=InstrutorProCNH Android Release,C=BR' -storepass:env INSTRUTORPRO_RELEASE_KEY_PASSWORD -keypass:env INSTRUTORPRO_RELEASE_KEY_PASSWORD
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar a chave de release.' }
        ConvertTo-SecureString $password -AsPlainText -Force | ConvertFrom-SecureString | Set-Content -LiteralPath $passwordFile -NoNewline
    } finally {
        Remove-Item Env:\INSTRUTORPRO_RELEASE_KEY_PASSWORD -ErrorAction SilentlyContinue
        $password = $null
    }
}

if (Test-Path $signedApk) { throw "O APK de distribuição já existe: $signedApk. Não será sobrescrito." }
if (Test-Path $alignedApk) { throw "O APK alinhado já existe: $alignedApk. Verifique antes de prosseguir." }

Push-Location (Join-Path $repoRoot 'frontend\android')
try {
    $previousAndroidHome = $env:ANDROID_HOME
    $env:ANDROID_HOME = $sdkRoot
    & .\gradlew.bat assembleRelease
    if ($LASTEXITCODE -ne 0) { throw 'Falha no build Android release.' }
} finally {
    $env:ANDROID_HOME = $previousAndroidHome
    Pop-Location
}

if (-not (Test-Path $unsignedApk)) { throw 'O build não produziu o APK unsigned esperado.' }
& (Join-Path $buildTools 'zipalign.exe') -p 4 $unsignedApk $alignedApk
if ($LASTEXITCODE -ne 0) { throw 'Falha ao alinhar o APK.' }

$securePassword = Get-Content -LiteralPath $passwordFile -Raw | ConvertTo-SecureString
try {
    $env:INSTRUTORPRO_RELEASE_KEY_PASSWORD = [System.Net.NetworkCredential]::new('', $securePassword).Password
    & (Join-Path $buildTools 'apksigner.bat') sign --ks $keyFile --ks-type PKCS12 --ks-key-alias $alias --ks-pass env:INSTRUTORPRO_RELEASE_KEY_PASSWORD --key-pass env:INSTRUTORPRO_RELEASE_KEY_PASSWORD --out $signedApk $alignedApk
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao assinar o APK.' }
} finally {
    Remove-Item Env:\INSTRUTORPRO_RELEASE_KEY_PASSWORD -ErrorAction SilentlyContinue
    $securePassword.Dispose()
}

& (Join-Path $buildTools 'apksigner.bat') verify $signedApk
if ($LASTEXITCODE -ne 0) { throw 'A assinatura do APK não foi validada.' }

$analyzer = Join-Path $sdkRoot 'cmdline-tools\latest\bin\apkanalyzer.bat'
$applicationId = (& $analyzer manifest application-id $signedApk).Trim()
$debuggable = (& $analyzer manifest debuggable $signedApk).Trim()
if ($applicationId -ne 'br.com.instrutorprocnh.app' -or $debuggable -ne 'false') {
    throw "APK inválido para distribuição: applicationId=$applicationId, debuggable=$debuggable"
}

$sha256 = (Get-FileHash -LiteralPath $signedApk -Algorithm SHA256).Hash
Remove-Item -LiteralPath $alignedApk
if (Test-Path "$signedApk.idsig") { Remove-Item -LiteralPath "$signedApk.idsig" }
Write-Output "APK_RELEASE=$signedApk"
Write-Output "SHA256=$sha256"
Write-Output "SIGNING_KEY=$keyFile"
Write-Output "SIGNING_PASSWORD_DPAPI=$passwordFile"
