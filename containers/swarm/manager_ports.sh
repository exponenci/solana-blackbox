firewall-cmd --add-port=2376/tcp --permanent;
firewall-cmd --add-port=2377/tcp --permanent;
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

# # to init manager node in cluster 
# docker swarm init --advertise-addr 192.168.100.12 # note that we use here same manager addr

# # to create overlay network
# docker network create --opt encrypted -d overlay --attachable solana_net

