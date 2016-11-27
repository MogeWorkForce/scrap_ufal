# scrap_ufal
## Documentação em construção (Já apresentado o TCC =D )
Para conseguir rodar o script, efetuar o seguinte comando, com python (2.7.X) instalado na sua máquina:

0 - Instalar o pip na sua máquina:
  - Recomendo seguir o tutorial de instalação do próprio site do Pip: https://pip.pypa.io/en/stable/installing/#install-pip
  - Debian e Ubuntu: sudo apt-get install python-pip

1 - Instalando o virtualenv via pip
  * (sudo) pip install virtualenv.
  
2 - Criando a virtualenv:
  - virtualenv NOME_DA_VIRTUALENV
  * ex:    virtualenv VenvUfal


3 - Ativando a virtualenv (estando no mesmo diretório):
  - source ./NOME_DA_VIRTUALENV/bin/activate (Unix e Mac)
  - NOME_DA_VIRTUALENV\Scripts\activate (Windows)
  
4 - pip install -r requeriments.txt

Se tiver problemas de como trabalhar com virtualenvs no Windows, recomendo ler este link:
- http://fernandofreitasalves.com/tutorial-virtualenv-para-iniciantes-windows/

6 - Etapas concluídas até o momento:
  * Captura dos dados, levando em consideração a pagina 1 da nota de empenho. Paginação aplicada, caso tenha mais de 1 página a nota de Empenho.
  * Captura dos documentos relacionados, apenas printando o resultado no momento.
  * Gerar um Json resultante.
  * Evitar um loop infinito ao acessar um documento relacionado.
  * Persistência dos dados, gerar uma interface de conexão ao Banco de Dados.
  * Banco de Dados, inicialmente MongoDB.
  * Paralelizar a captura dos dados (aplicada aos Documentos Relacionados).
  * Engenharia reversa (dada uma Nota de Liquidação/Pagamento ou Empenho (espécie: Reforço)) capturar todos os dados gerando o conteúdo da Nota de Empenho Original.
  * Adicionado o shutdown do crawler por configurações via banco.
  * Inserir novas Urls via API
  * Visualizar dados gerais em curso.
  * Saber quantos Documentos foram inseridos nos últimos X dias.
  
7 - Próximos passos:
  * Interface para introduzir "Regras".
  * Interface Web:
    * Introduzir novas Urls
    * Visualizar quantas Urls foram processadas nos últimos 7 dias (fallback ou principal).
    * Consulta de Documentos em específico.

8 - Como rodar:
  * python main.py -u "URL" -b BATCH
    * URL: Url que irá ser processada, salvando o documento e abrindo espaço para o processamento de novas Urls (vindas dos Documentos Relacionados), enfileirando numa queue.
    * BATCH: Número entre 1 à 20, será a quantidade de URLs vindas das queues e fallback para serem processadas.
