addpath(genpath('methods'));

%HOSTNAME = getenv("MATLAB_SERVER_HOSTNAME");
%ADDRESS = getenv("MATLAB_SERVER_ADDRESS");
%PORT = getenv("MATLAB_SERVER_PORT");

HOSTNAME = "DESKTOP-NOFUBS9";
ADDRESS = resolvehost(HOSTNAME,"address");
PORT = 9889;
DEBUG = 1;

server_inst = tcpserver(ADDRESS,PORT,"ConnectionChangedFcn",@connectionFcn);


function [X, y, target_count]=receive_call_data(src_connection)
    dimensions = read(src_connection,3,"int32");
    N = dimensions(1);
    d = dimensions(2);
    target_count = dimensions(3);
    X = read(src_connection,N*d,"double");
    X = reshape(X, N, d);
    y = read(src_connection,N,"double");
    y = reshape(y, N, 1);
end


function connectionFcn(src, ~)
global DEBUG;
if DEBUG == 1
    disp("Client connected");
end
if src.Connected
    method_name_no = read(src,1,"int32");
    if method_name_no == -1
        return
    end
    if method_name_no == 1 || method_name_no == 2 || method_name_no == 3
        if DEBUG == 1
            disp("receiving data for all methods");
        end
        [X, y, target_count] = receive_call_data(src);
        if DEBUG == 1
            disp("running method...");
        end
        if method_name_no == 1
            result = run_analysis_method(X, y, target_count, "PCE");
        elseif method_name_no == 2
            result = run_analysis_method(X, y, target_count, "GP");
        else
            result = run_analysis_method(X, y, target_count, "PC-GP");
        end
        if result.errorOccured == 1
            if DEBUG == 1
                disp("error occured");
            end
            write(src, 1, "int32"); 
            write(src, "[matlab] some error occured during calculation");
        else
            if DEBUG == 1
                disp("returning result...");
                % disp(SAresult.target_params);
            end

            %xvec = reshape(SAresult.target_params.', 1, []);
            %y = typecast(xvec, 'int32').';
            write(src, 0, "int32");
            write(src, result.target_params, 'double');

            if DEBUG == 1
                disp("calculations finished & results returned");
            end
        end
    else
        if DEBUG == 1
            disp(["No such meta-analysis method is available", method_name_no]);
        end
        write(src, 1, "int32"); 
        write(src, "[matlab] No such meta-analysis method is available");
    end
end
end
