### Instalação

A instação foi realizada/testada no Ubuntu 18.04.

Para uma instalação padrão:

```cmd
# para todos os comandos é esperado utilizar o usuário SU

# atualize o sistema
apt-get -y update
apt update

# instale o postgres (testado com o 12) conforme instruções https://www.postgresql.org/download/linux/ubuntu/

# instale os requisitos do Helios
apt-get -y install python2.7 python-pip gettext

# crie um usuário para o helios
useradd -m -k /etc/skel/ -s /bin/bash helios

# vá para o diretório do usuário criado
cd /home/helios/

# clone este repositório na pasta do usuário
git clone https://github.com/rosbso/helios-server.git

# vá para a pasta do servidor helios
cd helios-server/

# instale os requisitos do servidor
pip install -r requirements.txt

# dê acesso ao usuário do helios sobre as pastas
chown -R helios:helios /home/helios/
```

### Servidor de desenvolvimento

Para levantar o servidor em modo de desenvolvimento:

```cmd
# troque para o usuário do helios
su helios

# execute o script para TESTE
./run.sh

# para finalizar basta executar Ctrl + C no terminal aberto para finalizar o script
```

### Servidor de produção

#### Para levantar o servidor em modo de produção:

```cmd
# instale os módulos necessários para servir os scripts python https://tecadmin.net/install-apache-mod-wsgi-on-ubuntu-18-04-bionic/
apt-get update
apt-get install libexpat1

# apache (2.4.29) e alguns pré-requisitos
apt-get install apache2 apache2-utils ssl-cert

# mod_wsgi
apt-get install libapache2-mod-wsgi

# reinicie o apache
systemctl restart apache2
```

#### Para verificar o funcionamento:

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

#### Para servir o Helios pelo Apache:

```cmd
# crie a pasta da aplicação
mkdir /var/www/apps/helios-ldap

# copie os arquivos para o diretório www
cp -r /home/helios/helios-ldap/* /var/www/apps/helios-ldap/

# se necessário, apague o arquivo existente antes de copiar
cd /var/www/apps
rm -r -f helios-ldap

# configure o Apache para servir o Django
nano /etc/apache2/conf-available/mod-wsgi.conf

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
```

#### Para configurar o celery

```cmd
# com o usuário root, edite o crontab
crontab -e

# e adicione as linhas abaixo. a primeira é para executar o script em caso de reboot, a outra é executada de 20 em 20min
@reboot /var/www/apps/helios-ldap/check-services.sh >/dev/null 2>&1
*/20 * * * *  /var/www/apps/helios-ldap/check-services.sh >/dev/null 2>&1

# configure o crontab para iniciar no boot
update-rc.d cron defaults
```

### Break in case of emergency

Desinstala tudo instalado no pip:

```cmd
pip freeze | xargs pip uninstall -y
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
nano /var/log/apache2/error.log
```