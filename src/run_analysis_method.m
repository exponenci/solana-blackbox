function SAresult=run_analysis_method(X, y, target_count, method_name)
    uqlab;
    tic
    % https://www.mathworks.com/content/dam/mathworks/guide-or-book/matlab-production-server-guide.pdf
    % https://www.mathworks.com/matlabcentral/answers/328959-how-to-call-functions-from-another-m-file
    [Nset, dset] = size(X);
    disp(['[#', method_name, '] N=',num2str(Nset),' and d=',num2str(dset)])

    SAresult.errorOccured=0;

    input.X=X;
    input.y=y;
    try
        if strcmp(method_name,"PCE")
            outPCE=PCESA(input);
            STs=outPCE.SA.Results.Total;
            SAresult.time=outPCE.time;
        elseif strcmp(method_name,"GP")
            outGP=GPSA_UQ(input);
            STs=outGP.SA.Results.Total;
            SAresult.time=outGP.time;
        elseif strcmp(method_name,"PC-GP")
            outPCGP=PCEGPSA_UQ(input);
            STs=outPCGP.SA.Results.Total;
            SAresult.time=outPCGP.time;
        else
            disp('unknown method')
            SAresult.errorOccured=1;
        end
    catch
        disp('method did not work for some reason. Moving on.')
        STs=zeros(dset,1); % put in some zeros to stop errors later on.
        SAresult.errorOccured=1;
    end


    [~,STord]=sort(STs,1,'descend'); % sort measure by descending order
    SAresult.target_params=STord(1:target_count);

    toc
