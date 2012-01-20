Sitio de SHDH Puebla
=====================

El sitio está hecho en `Python`_ usando el entorno de desarrollo web `Pyramid`_, a continuación se muestra es procedimiento para instalar el sitio::

    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py shdhpuebla-site
    $ cd shdhpuebla-site
    $ . bin/activate
    $ git clone git://github.com/erikriver/shdhpuebla.git
    $ pip install shdhpuebla/
    $ populate_shdhpuebla development.ini
    $ pserve development.ini

Producción
-----------

Para poner es sitio en producción es el mismo procedimiento anterior pero ahora se ejecuta con otro archivo de configuración.::

    $ pserve production.ini --daemon

Servidor Web
-------------

La configuración par servidor web `Nginx`_ en modo proxy a la aplicación web puede quedar así::

    server {
        listen 80;
        server_name www.shdhpuebla.org shdhpuebla.org;

        location / {
            proxy_set_header        Host $host;
            proxy_set_header        X-Real-IP $remote_addr;
            proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header        X-Forwarded-Proto $scheme;

            client_max_body_size    10m;
            client_body_buffer_size 128k;
        
            proxy_connect_timeout   60s;
            proxy_send_timeout      90s;
            proxy_read_timeout      90s;
            proxy_buffering         off;
            proxy_temp_file_write_size 64k;

            proxy_pass  http://0.0.0.0:6543;
            proxy_redirect  default;
        }

    }

Cualquier comentario acerca del sitio es bienvenido.

.. _`Python`: http://python.org/
.. _`Pyramid`: http://www.pylonsproject.org/projects/pyramid/about
.. _`Nginx`: http://nginx.org/
