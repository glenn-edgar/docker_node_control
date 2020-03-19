FROM redis
VOLUME [/data,/usr/local/etc/redis/redis.conf]
EXPOSE 6379
ENTRYPOINT ["redis-server", "--lsappendonly yes"]
  