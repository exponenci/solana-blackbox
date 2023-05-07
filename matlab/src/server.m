hostname = "DESKTOP-NOFUBS9";
address = resolvehost(hostname,"address");
server_inst = tcpserver(address,9889,"ConnectionChangedFcn",@connectionFcn);

function [X, y, target_count]=receive_settings(src)
    disp("receiving methods run info...");
    %write(src, "[matlab]Send N (runs count) and d (params count) values");
    dimensions = read(src,2,"int32");
    N = dimensions(1);
    d = dimensions(2);
    disp(["dimensions", N, d]);
    %write(src, "[matlab]Send X matrix (shape=Nxd)");
    X = read(src,N*d,"double");
    X = reshape(X, N, d);
    disp(X);
    %write(src, "[matlab]Send Y matrix (shape=Nx1)");
    y = read(src,N,"double");
    y = reshape(y, N, 1);
    disp(y);
    %write(src, "[matlab]Send count of params to be chosen");
    target_count = read(src,1,"int32");
    disp(target_count);
    %write(src, "[matlab]All data is received");
    disp("methods run info received");
end
function connectionFcn(src, ~)
disp("Client connected");
while src.Connected
    %write(src, "[matlab]Hello from matlab server!\nSend 1, 2 or 3 for choosing meta-analysis method (PCE, GP, PC-GP)");
    method_name_no = read(src,1,"int32");
    if method_name_no == 1 || method_name_no == 2 || method_name_no == 3
        [X, y, target_count] = receive_settings(src);
        disp("running method...");
        if method_name_no == 1
            result = run_analysis_method(X, y, target_count, "PCE");
        elseif method_name_no == 2
            result = run_analysis_method(X, y, target_count, "GP");
        else
            result = run_analysis_method(X, y, target_count, "PC-GP");
        end
        if result.errorOccured == 1
            disp("error occured");
            write(src, "[matlab]error occured");
        else
            disp("returning value...");
            % disp(SAresult.target_params);
            %xvec = reshape(SAresult.target_params.', 1, []);
            %y = typecast(xvec, 'int32').';
            disp(class(result.target_params));
            disp(result.target_params);
            for ii = 1:target_count
                disp([ii, class(result.target_params(ii))]);
                write(src, result.target_params(ii), 'double');
            end
            disp("value returned");
        end
    else
        disp(["No such meta-analysis method is available", method_name_no]);
        write(src, "No such meta-analysis method is available")
    end
end
end