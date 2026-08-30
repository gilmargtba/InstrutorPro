# Malha das unidades federativas do Brasil

`br-ufs.geojson` foi obtido da API de Malhas Geográficas do IBGE em 30/08/2026:

`https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=UF`

O arquivo contém as 27 unidades federativas na qualidade mínima oferecida pelo serviço e é
empacotado localmente para que o mapa demonstrativo não dependa de uma chamada externa em tempo de
execução. As contagens exibidas pela aplicação não vieram do IBGE: são fixtures sintéticas da demo.
