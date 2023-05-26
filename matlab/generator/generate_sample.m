function [] = generate_sample(Nlow, Nhigh, dlow, dhigh, Nexp)
    % set 0 to allow N to be less then d, otherwise set non-zero value
    updateDimensions = 0;

    % metainformation for y-function
    basehold = 0; % set 0 to include all basic functions
    inter2=0.5; % fraction (of d) of 2 way interactions (e.g. if d=10 and inter2=0.5, there will be 5 2-way interaction terms
    inter3=0.2; % same for 3 way.
    
    % the following are parameters for the randnmix function, mixture of two
    % normal dists.
    sig1=0.5;
    sig2=5;
    phimix=0.7;
    
    Xmeta=rand(Nexp,2); % to store actual dimentions of X
    Xmeta=[Xmeta(:,1)*(Nhigh-Nlow)+Nlow,Xmeta(:,2)*(dhigh-dlow)+dlow];
    Xmeta=floor(Xmeta);
    Xp=1;
    while Xp<Nexp+1 % using a while statement here because need a way to redo iteration under certain circumstances (see below)
        while updateDimensions && Xmeta(Xp,1)/(Xmeta(Xp,2)+1)<1 % if less than one (k+1) design
            Xmeta(Xp,:)=rand(1,2); % generate new values
            Xmeta(Xp,:)=[Xmeta(Xp,1)*(Nhigh-Nlow)+Nlow,Xmeta(Xp,2)*(dhigh-dlow)+dlow];
            Xmeta(Xp,:)=floor(Xmeta(Xp,:));
        end
        NN=Xmeta(Xp,1); % the sample size for this experiment
        dd=Xmeta(Xp,2); % the dimensionality for this experiment
        XsobMM=lhsdesign(NN,dd,'iterations',100);


        Ninter2=floor(dd*inter2); % round down to nearest integer.
        Ninter3=floor(dd*inter3);
        if basehold==0 % include all basis functions
            noFXflag=1;
            while noFXflag==1 % just regenerates basis functions in case all of them are 7 (no effect), which causes an error in UQLab, amongst other things.
                para_f1=randi(9,dd,1); % these numbers dictate which basis function is associated with each Xi
                if sum((para_f1==7))<dd; noFXflag=0; end
            end
        else % hold out one
            noFXflag=1;
            while noFXflag==1 % same deal as above
                para_f1=randi(8,dd,1);
                para_f1(para_f1>=basehold)=para_f1(para_f1>=basehold)+1; %
                if sum((para_f1==7))<dd; noFXflag=0; end
            end
        end
        para_f2=randi(dd,Ninter2,2); % the 2-way interactions (variable indices)
        para_f3=randi(dd,Ninter3,3); % the 3-way interactions (variable indices)
        para_a=randnmix(sig1,sig2,phimix,sum([length(para_f1),size(para_f2,1),size(para_f3,1)]),0);
    
        % bits for MCSA
        MCSAinput.modname='monsterfunc';
        MCSAinput.mpars.a=para_a;
        MCSAinput.mpars.f1=para_f1;
        MCSAinput.mpars.f2=para_f2;
        MCSAinput.mpars.f3=para_f3;
        % evaluate function for non-MCSA methods
        ysobMM=monsterfunc(XsobMM,MCSAinput.mpars);
        
        % save generated data
        writematrix(XsobMM, 'Xmatrix' + string(Xp));
        writematrix(ysobMM, 'ymatrix' + string(Xp));
        Xp = Xp + 1;
    end
end
