firewall-cmd --add-port=2376/tcp --permanent;
firewall-cmd --add-port=7946/tcp --permanent;
firewall-cmd --add-port=7946/udp --permanent;
firewall-cmd --add-port=4789/udp --permanent;
firewall-cmd --reload;

systemctl restart docker;

# # to join to cluter run command that was received via `docker swarm init`
# # expample: docker swarm join --token <TOKEN> <MANAGER_ADDR>:2377
