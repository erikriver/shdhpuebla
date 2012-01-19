shdhpuebla README
==================

Getting Started
---------------

    $ curl -O https://raw.github.com/pypa/virtualenv/master/virtualenv.py
    $ python virtualenv.py shdhpuebla-site
    $ cd shdhpuebla-site
    $ . bin/activate
    $ git clone git://github.com/erikriver/shdhpuebla.git
    $ pip install shdhpuebla/
    $ populate_shdhpuebla development.ini
    $ pserve development.ini

Production
--------------

    $ pserve production.ini --daemon

Nginx config
-------------

    server {
        listen 80;
        server_name www.shdhpuebla.org www.shdhpuebla.com shdhpuebla.org shdhpuebla.com;

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

    }

