server = tcpserver('localhost',9889,"ConnectionChangedFcn",@connectionFcn)

function [X, y, target_count]=receive_settings(src, method_name)
    disp("receiving methods run info...");
    write(src, "[matlab]Send N (runs count) and d (params count) values");
    [N, d] = read(src,2,"int32");
    write(src, "[matlab]Send X matrix (shape=Nxd)");
    X = read(src,N*d,"int32");
    write(src, "[matlab]Send Y matrix (shape=Nx1)");
    y = read(src,N,"int32")
    write(src, "[matlab]Send count of params to be chosen");
    target_count = read(src,1,"int32")
    disp("methods run info received");
end

function connectionFcn(src, ~)
disp("Client connected");
if src.Connected
    write(src, "[matlab]Hello from matlab server!\nSend 1, 2 or 3 for choosing meta-analysis method (PCE, GP, PC-GP)");
    method_name_no = read(src,1,"int32");
    if method_name_no == 1 || method_name_no == 2 || method_name_no == 3
        [X, y, target_count] = receive_settings(src)
        disp("running method...");
        if method_name_no == 1
            result = run_analysis_method(X, y, target_count, "PCE");
        elseif method_name_no == 2
            result = run_analysis_method(X, y, target_count, "GP");
        else
            result = run_analysis_method(X, y, target_count, "PC-GP");
        end
        if result.errorOccured == 1:
            disp("error occured");
            write(src, "[matlab]error occured");
        else
            disp("returning value...");
            write(src, SAresult.target_params);
            disp("value returned");
        end
    else
        write(src, "No such meta-analysis method is available")
    end
end
end