firewall-cmd --add-port=2376/tcp --permanent;
firewall-cmd --add-port=2377/tcp --permanent;
firewall-cmd --add-port=7946/tcp --permanent;
firewall-cmd --add-port=7946/udp --permanent;
firewall-cmd --add-port=4789/udp --permanent;
firewall-cmd --reload;

systemctl restart docker;

# # to init manager node in cluster 
# docker swarm init

# # to create overlay network
# docker network create --opt encrypted -d overlay --attachable solana_net
