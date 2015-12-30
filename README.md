# scrap_ufal
## Documentação em construção
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
  - source ./NOME_DA_VIRTUALENV/bin/activate (Unix)
  - NOME_DA_VIRTUALENV\Scripts\activate
  
4 - pip install -r requeriments.txt

Se tiver problemas de como trabalhar com virtualenvs no Windows, recomendo ler este link:
- http://fernandofreitasalves.com/tutorial-virtualenv-para-iniciantes-windows/

6 - Etapas concluídas até o momento:
  * Captura dos dados, levando em consideração a pagina 1 da nota de empenho. Paginação aplicada, caso tenha mais de 1 página a nota de Empenho.
  * Captura dos documentos relacionados, apenas printando o resultado no momento.
  * Gerar um Json resultante.
  * Evitar um loop infinito ao acessar um documento relacionado.

7 - Próximos passos:
  * Persistência dos dados, gerar uma interface de conexão ao Banco de Dados.
  * Decidir qual o banco de dados será utilizado (inicialmente MongoDB está nos planos).
  * Interface para introduzir "Regras".
  * Paralelizar a captura dos dados (aplicada aos Documentos Relacionados).
  * Engenharia reversa (dada uma Nota de Liquidação/Pagamento ou Empenho (espécie: Reforço)) capturar todos os dados gerando o conteúdo da Nota de Empenho Original.
