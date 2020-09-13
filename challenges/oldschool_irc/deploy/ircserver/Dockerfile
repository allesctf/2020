FROM inspircd/inspircd-docker

USER root
COPY config/ /inspircd/conf/
RUN set -x && \
	chown -R inspircd: /inspircd/conf && \
	chmod a+x /inspircd/conf/*.sh
USER inspircd

HEALTHCHECK NONE

ENTRYPOINT ["/entrypoint.sh"]
