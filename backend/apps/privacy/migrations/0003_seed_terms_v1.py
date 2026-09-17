# ruff: noqa: E501
import hashlib

from django.db import migrations
from django.utils import timezone

STUDENT_TERMS = """1. Objeto
O InstrutorProCNH é uma plataforma digital destinada a facilitar a localização e o contato entre pessoas interessadas em serviços relacionados à aprendizagem de direção e profissionais disponibilizados na plataforma.

2. Cadastro
O usuário deverá fornecer informações verdadeiras, completas e atualizadas quando optar por criar uma conta. O usuário é responsável pela segurança de suas credenciais de acesso.

3. Busca sem cadastro
Quando tecnicamente disponibilizada, a busca de instrutores e a visualização de perfis públicos poderão ocorrer sem criação de conta.

4. Localização
A localização do dispositivo somente será solicitada mediante ação explícita do usuário. Alternativas como cidade, bairro ou CEP poderão ser utilizadas quando disponíveis.

5. Instrutores
A plataforma poderá apresentar informações profissionais, regiões de atendimento, categorias, veículos, preços indicativos e outros dados autorizados para publicação. Informações somente serão apresentadas como verificadas quando houver efetiva verificação registrada no sistema.

6. Contato via WhatsApp
O InstrutorProCNH poderá disponibilizar botão para iniciar contato com o instrutor por meio do WhatsApp, serviço externo operado por terceiro. A plataforma poderá registrar o evento de intenção de contato para métricas e segurança, mas não lê nem armazena o conteúdo das conversas realizadas no WhatsApp.

7. Contratação do serviço
No MVP atual, o contato iniciado pelo InstrutorProCNH não representa automaticamente contratação, pagamento ou confirmação de aula. Condições comerciais acordadas externamente deverão ser tratadas pelas partes, salvo quando a plataforma disponibilizar funcionalidade específica.

8. Responsabilidades do usuário
O usuário deverá fornecer informações verdadeiras, utilizar a plataforma de maneira lícita, respeitar os demais usuários, não tentar acessar contas ou dados de terceiros e não utilizar a plataforma para fraude, assédio ou finalidade ilícita.

9. Disponibilidade
A plataforma poderá passar por manutenção, atualização ou indisponibilidade temporária.

10. Privacidade
O tratamento de dados pessoais será realizado conforme a Política de Privacidade vigente do InstrutorProCNH e a legislação aplicável.

11. Direitos sobre dados pessoais
O usuário poderá utilizar os mecanismos disponibilizados pela plataforma ou o canal de privacidade para exercer os direitos aplicáveis previstos na legislação.

12. Alterações
Os Termos poderão ser atualizados. Quando uma alteração exigir novo aceite, o sistema solicitará aceite da nova versão antes da continuidade das funcionalidades dependentes.

13. Encerramento
O usuário poderá solicitar encerramento ou exclusão da conta, observadas as hipóteses legais de conservação de determinados registros.

14. Contato
focusgtba@gmail.com"""


INSTRUCTOR_TERMS = """1. Objeto
O InstrutorProCNH oferece infraestrutura digital para que profissionais elegíveis possam cadastrar informações profissionais e, quando aprovados para publicação, ser encontrados por potenciais alunos.

2. Cadastro profissional
O instrutor declara que as informações fornecidas devem ser verdadeiras, completas e atualizadas.

3. Credenciamento
O cadastro na plataforma não substitui autorização, credenciamento, habilitação, certificado, registro ou exigências do órgão de trânsito competente. A publicação poderá depender de verificação e decisão administrativa do InstrutorProCNH.

4. Elegibilidade
A existência de conta ou preenchimento do cadastro não garante publicação. A publicação poderá depender de conta ativa, papel profissional válido, perfil completo, verificação, elegibilidade, PublicationDecision APPROVED, região autorizada e inexistência de suspensão ou expiração.

5. Informações profissionais
O instrutor é responsável por manter atualizados, quando aplicáveis, WhatsApp, preço, duração comercial, categorias, transmissão, veículo e região de atendimento.

6. Alterações relevantes
Alterações em categoria, veículo, transmissão, credenciamento ou outros dados sujeitos a verificação poderão provocar nova análise e suspensão temporária da publicação.

7. Documentos
O InstrutorProCNH somente receberá documentos reais quando a capability correspondente estiver autorizada. Enquanto REAL_DOCUMENT_UPLOADS=false, o sistema não solicitará envio por mecanismo inseguro.

8. Perfil público
Somente dados autorizados poderão ser exibidos. Não serão publicados CPF, CNH, CRLV, número completo de credencial, certificados privados, endereço residencial, placa completa ou documentos originais.

9. Localização
A localização residencial não será utilizada como localização pública. A plataforma utilizará região ou localização de atendimento autorizada.

10. WhatsApp
O perfil poderá permitir contato via WhatsApp. A plataforma poderá registrar métricas de intenção de contato, mas não lê as conversas externas.

11. Relação profissional
O instrutor permanece responsável pelo cumprimento das obrigações profissionais, legais, regulatórias, tributárias e de trânsito aplicáveis à sua atuação. Estes Termos não criam automaticamente relação trabalhista.

12. Preço
Os preços apresentados devem corresponder às informações fornecidas pelo profissional. No MVP atual, a plataforma não processa pagamento nem garante conversão do contato em contratação.

13. Avaliações
Não serão criadas avaliações fictícias nem apresentadas notas inventadas.

14. Suspensão
A plataforma poderá suspender ou retirar a publicação por perda de elegibilidade, credenciamento inválido ou expirado, informação material incorreta, violação dos Termos, risco de segurança, obrigação legal ou regulatória ou decisão administrativa registrada. Ações administrativas relevantes serão auditadas.

15. Privacidade
O tratamento dos dados pessoais seguirá a Política de Privacidade vigente e a legislação aplicável.

16. Encerramento
O instrutor poderá solicitar encerramento da conta, observadas obrigações legais, registros de auditoria e hipóteses legítimas de conservação.

17. Alterações dos Termos
Nova versão materialmente relevante poderá exigir novo aceite.

18. Contato
focusgtba@gmail.com"""


def seed_terms(apps, schema_editor):
    LegalDocument = apps.get_model("privacy", "LegalDocument")
    effective_at = timezone.now()
    for audience, title, content in (
        ("STUDENT", "Termos de Uso — Aluno — InstrutorProCNH", STUDENT_TERMS),
        ("INSTRUCTOR", "Termos de Uso — Instrutor — InstrutorProCNH", INSTRUCTOR_TERMS),
    ):
        LegalDocument.objects.create(
            document_type="TERMS",
            audience=audience,
            version="1.0",
            title=title,
            content=content,
            content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
            effective_at=effective_at,
            is_active=True,
        )


class Migration(migrations.Migration):
    dependencies = [("privacy", "0002_legaldocument_legalacceptancerecord")]

    operations = [migrations.RunPython(seed_terms, migrations.RunPython.noop)]
