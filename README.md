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
