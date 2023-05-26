ARG MLM_LICENSE_FILE=/licenses/network.lic

FROM mathworks/matlab:r2021b

ARG MLM_LICENSE_FILE

WORKDIR /app

COPY src/methods/ methods/
COPY src/server.m server.m
COPY src/run_analysis_method.m run_analysis_method.m
COPY libs/uqlab libs/uqlab
COPY network.lic /licenses/network.lic

ENV MLM_LICENSE_FILE=${MLM_LICENSE_FILE}

RUN [ "uqlab" ]
CMD [ "server" ]
