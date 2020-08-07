# Instalação

A instação foi realizada/testada no Ubuntu 18.04.

## Para uma instalação padrão

```cmd
# atualize o sistema
sudo apt-get -y update
sudo apt update

# crie um usuário para o helios
sudo useradd -m -k /etc/skel/ -s /bin/bash helios

# adiciona ele como sudo
sudo adduser helios sudo

#ou
usermod -a -G sudo usuario
```

### Instale e configure o Postgres-12

```cmd
# instale o postgres (testado com o 12) conforme instruções https://www.postgresql.org/download/linux/ubuntu/
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

# Import the repository signing key:
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update the package lists:
sudo apt-get update

# Install the latest version of PostgreSQL.
# If you want a specific version, use 'postgresql-12' or similar instead of 'postgresql':
sudo apt-get install postgresql-12

# reinicie o banco
sudo pg_ctlcluster 12 main restart

# verifica o status do banco
sudo pg_ctlcluster 12 main status

# libere o acesso ao localhost editando o arquivo
sudo nano /etc/postgresql/12/main/postgresql.conf

# e descomente a linha
listen_addresses = 'localhost'

# libere o acesso ao banco para o usuário helios editando o arquivo
sudo nano /etc/postgresql/12/main/pg_hba.conf

# e incluindo a linha abaixo logo acima de 'local all all peer'
local all helios md5

# reinicie novamente o banco
sudo pg_ctlcluster 12 main restart

# crie um usuário para o helios no banco
sudo -u postgres createuser -S -d -R -P helios
```

### Continue a instalação do Helios

```
# instale os requisitos do Helios
sudo apt-get -y install python2.7 python-pip gettext
sudo apt-get install python-ldap python-dev libsasl2-dev libldap2-dev

# copie os dados de conexão para a pasta do usuário helios

# dê acesso ao usuário do helios sobre as pastas
sudo chown -R helios:helios /home/helios/

# alterne para o usuário criado

# vá para o diretório do usuário criado
cd /home/helios/

# clone este repositório na pasta do usuário
git clone https://github.com/ufmt-ces/helios-server-publico.git

# vá para a pasta clonada
cd helios-server-publico/

# dê permissão de execusão para os arquivos
sudo chmod +x check-services.sh

# instale os requisitos do helios
sudo pip install -r requirements.txt

# atualiza a biblioteca pyscopg2 para a versão mais recente (2-2.8.5)
sudo pip uninstall psycopg2
sudo apt-get install libpq-dev
sudo pip install psycopg2

# sobreponha as configurações com os dados de conexão com a UFMT
cp /home/helios/settings.py settings.py

# lista o bancos existentes
sudo -u postgres psql -l

# crie um banco para o helios
createdb -h localhost -U helios -W helios

# popule o banco
sudo python manage.py syncdb
sudo python manage.py migrate

# compile a tradução
sudo python manage.py compilemessages
```

### Teste local

Para testar localmente:

```cmd
cd /home/helios/helios-server-publico/
sudo python manage.py runserver 0.0.0.0:80

# para finalizar basta executar Ctrl + C no terminal aberto para finalizar o script
```

### Configurar para produção

```cmd
# instale os módulos necessários para servir os scripts python https://tecadmin.net/install-apache-mod-wsgi-on-ubuntu-18-04-bionic/
sudo apt-get update
sudo apt-get install libexpat1

# apache (2.4.29) e alguns pré-requisitos
sudo apt-get install apache2 apache2-utils ssl-cert

# mod_wsgi
sudo apt-get install libapache2-mod-wsgi

# reinicie o apache
sudo systemctl restart apache2
```

### Para servir o Helios pelo Apache:

```cmd
# crie a pasta da aplicação
sudo mkdir /var/www/apps
sudo mkdir /var/www/apps/helios-ldap

# copie os arquivos para o diretório www
sudo cp -r /home/helios/helios-server-publico/* /var/www/apps/helios-ldap/

# se necessário, apague o arquivo existente antes de copiar
cd /var/www/apps
sudo rm -r -f helios-ldap
sudo mkdir /var/www/apps/helios-ldap

# configure o Apache para servir o Django
sudo nano /etc/apache2/conf-available/mod-wsgi.conf

# com as linhas
WSGIScriptAlias / /var/www/apps/helios-ldap/wsgi.py
WSGIPythonPath /var/www/apps/helios-ldap

<Directory /var/www/apps/helios-ldap>
<Files wsgi.py>
Require all granted
</Files>
</Directory>

Alias /media/js/ /var/www/apps/helios-ldap/sitestatic/js/
Alias /media/ /var/www/apps/helios-ldap/helios/media/
Alias /static/ /var/www/apps/helios-ldap/sitestatic/
Alias /booth/ /var/www/apps/helios-ldap/sitestatic/booth/
Alias /verifier/ /var/www/apps/helios-ldap/sitestatic/verifier/

# vá para o diretório www
cd /var/www/apps/helios-ldap/

# inicie o celery
sudo python manage.py celeryd --events --loglevel=INFO --concurrency=5 -f celery.log &

# depois habilite o módulo e reinice o apache
sudo a2enconf mod-wsgi # ou a2enmod wsgi?
sudo systemctl reload apache2

```

### Para manter o celery rodando:

```cmd
# vá para o diretório www
cd /var/www/apps/helios-ldap/

# edite o crontab
crontab -e

# e adicione as linhas abaixo. a primeira é para executar o script em caso de reboot, a outra é executada de 20 em 20min
@reboot /var/www/apps/helios-ldap/check-services.sh >/dev/null 2>&1
*/20 * * * *  /var/www/apps/helios-ldap/check-services.sh >/dev/null 2>&1

# dê permissão de execusão para o script
sudo chmod +x check-services.sh

# e configure o crontab para iniciar no boot
update-rc.d cron defaults
```

## Break in case of emergency

Desinstala tudo instalado no pip:

```cmd
sudo pip freeze | xargs sudo pip uninstall -y
```

Acompanha o [Crontab](https://askubuntu.com/questions/56683/where-is-the-cron-crontab-log):

```cmd
grep CRON /var/log/syslog
# ou
tail -f /var/log/syslog | grep CRON
```

Para visualizar os logs do celery:

```cmd
nano /var/www/apps/helios-ldap/celery.log
```

Para visualizar erros:

```cmd
sudo nano /var/log/apache2/error.log
```


### Para verificar o funcionamento do módulo mod_wsgi:

```cmd
# crie uma página html em python
nano /var/www/html/wsgi_test_script.py

# e adicione o conteúdo
def application(environ,start_response):
    status = '200 OK'
    html = '<html>\n' \
           '<body>\n' \
           ' Hooray, mod_wsgi is working\n' \
           '</body>\n' \
           '</html>\n'
    response_header = [('Content-type','text/html')]
    start_response(status,response_header)
    return [html]

# configure o Apache para servir esse arquivo
nano /etc/apache2/conf-available/mod-wsgi.conf

# adicionando a linha
WSGIScriptAlias /test_wsgi /var/www/html/wsgi_test_script.py

# depois habilite o módulo e reinice o apache
a2enconf mod-wsgi # ou a2enmod wsgi?
systemctl restart apache2

# a página será exibida em
http://SERVER_IP/test_wsgi
```