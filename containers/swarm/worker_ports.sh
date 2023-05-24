firewall-cmd --add-port=2376/tcp --permanent;
firewall-cmd --add-port=7946/tcp --permanent;
firewall-cmd --add-port=7946/udp --permanent;
firewall-cmd --add-port=4789/udp --permanent;
firewall-cmd --reload;

systemctl restart docker;

# # for all hosts: 
# cat >/etc/hosts <<EOF
# 192.168.100.12 manager
# 192.168.100.13 worker01
# 192.168.100.14 worker02 
# # etc.. add or change ip addresses of manager and worker nodes as you wish
# EOF 

# # to join to cluter run command that was received via `docker swarm init`
# # expample: docker swarm join --token <TOKEN> <MANAGER_ADDR>:2377
