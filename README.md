# **ai-sinkhole**
This project introduces a method for the discovery, classification, and blocking of emerging LLM chatbot services during proctored exams. This was made possible with Pi-hole, a DNS sinkhole that blocks unwanted content on your devices without installing any client-side software. This project was done by running Pi-hole in a Docker container. See the steps for installing Pi-hole in Docker below.
## **Installation**
### **Quick Start**
Using [Docker-compose](https://docs.docker.com/compose/install/):

1. Copy the below docker compose example and update as needed:

```yml
# More info at https://github.com/pi-hole/docker-pi-hole/ and https://docs.pi-hole.net/
services:
  pihole:
    container_name: pihole
    image: pihole/pihole:latest
    ports:
      # DNS Ports
      - "53:53/tcp"
      - "53:53/udp"
      # Default HTTP Port
      - "80:80/tcp"
      # Default HTTPs Port. FTL will generate a self-signed certificate
      - "443:443/tcp"
      # Uncomment the line below if you are using Pi-hole as your DHCP server
      #- "67:67/udp"
      # Uncomment the line below if you are using Pi-hole as your NTP server
      #- "123:123/udp"
    environment:
      # Set the appropriate timezone for your location (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), e.g:
      TZ: 'America/New_York'
      # Set a password to access the web interface. Not setting one will result in a random password being assigned
      FTLCONF_webserver_api_password: 'correct horse battery staple'
      # If using Docker's default `bridge` network setting the dns listening mode should be set to 'ALL'
      FTLCONF_dns_listeningMode: 'ALL'
    # Volumes store your data between container upgrades
    volumes:
      # For persisting Pi-hole's databases and common configuration file
      - './etc-pihole:/etc/pihole'
      # Uncomment the below if you have custom dnsmasq config files that you want to persist. Not needed for most starting fresh with Pi-hole v6. If you're upgrading from v5 you and have used this directory before, you should keep it enabled for the first v6 container start to allow for a complete migration. It can be removed afterwards. Needs environment variable FTLCONF_misc_etc_dnsmasq_d: 'true'
      #- './etc-dnsmasq.d:/etc/dnsmasq.d'
    cap_add:
      # See https://github.com/pi-hole/docker-pi-hole#note-on-capabilities
      # Required if you are using Pi-hole as your DHCP server, else not needed
      - NET_ADMIN
      # Required if you are using Pi-hole as your NTP client to be able to set the host's system time
      - SYS_TIME
      # Optional, if Pi-hole should get some more processing time
      - SYS_NICE
    restart: unless-stopped
```

2. Run `docker compose up -d` to build and start pi-hole (Syntax may be `docker-compose` on older systems).

> [!NOTE]
> Volumes are recommended for persisting data across container re-creations for updating images.

## **Loading Blocklists**
To load the blocklist you must first add the list's URL in the **Group Management > Adlists** section of the web interface. To do this, enter **https://raw.githubusercontent.com/aimledu/ai-sinkhole/refs/heads/main/blocklist/ai_services.txt** in the * *Address* * field, and enter **ai-sinkhole** in the * *Comment* * field. Adding the proper comment tag is essential for using our enabling/disabling scripts. After the previous steps have been completed, run **pihole -g** in the terminal or click **"Update"** in the **Tools > Update Gravity** section to finish loading the blocklist.

## **Enabling/Disabling Blocklists**
Blocklists can be enabled/disabled directly in the Pi-hole web UI by locating the blocklist and toggling the enable/disable option.
Alternatively, our scripts can be used to enable/disable individual blocklists for specified time ranges directly from the host machine.

### **Enabling/Disabling Blocklists with Scripts**
#### **blocking_timer.sh**
To use this script, run **./blocking_timer.sh** on the host machine. You will be prompted to tell the script what to do. If you want to disable the blocklist, enter **0**. If you want to enable the blocklist, enter **1**. You will then be asked to enter the duration. Be sure to specify the time unit (e.g. If you want 15 seconds, enter **15s**. If you want 15 minutes, enter **15m**. If you want 15 hours, enter **15h**.) After your specified duration is over, the blocklist will revert to its original state.
#### **enable.sh**
To use this script, run **./enable.sh** on the host machine. This will enable the wordlist indefinitely.
#### **disable.sh**
To use this script, run **./disable.sh** on the host machine. This will disable the wordlist indefinitely.
