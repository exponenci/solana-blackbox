function SAout=metafunction_comparison(Nexp)

uqlab;

%% Meta Experimental Design
Nset = 10;
dset = 89;
NMCSAtrue=10000; % the number of (k+1) designs to use in estimation of "true" ST values.
STcut=0.1; % this is a parameter to control how many variables to count as "important". Basically the fraction of the sum of ST which we want to keep in.

SAout.MetaExp.Nexp=Nexp;
SAout.MetaExp.Nset=Nset;
SAout.MetaExp.dset = dset;
SAout.MetaExp.NMCSAtrue=NMCSAtrue;
SAout.MetaExp.STcut=STcut;

% Nset, dset, Nexp

%%% Metafunction settings
inter2=0.5; % fraction (of d) of 2 way interactions (e.g. if d=10 and inter2=0.5, there will be 5 2-way interaction terms
inter3=0.2; % same for 3 way.
sig1=0.5;
sig2=5;
phimix=0.7;

SAout.Metafunc.Dist.d2=inter2;
SAout.Metafunc.Dist.d3=inter3;
SAout.Metafunc.Dist.sig1=sig1;
SAout.Metafunc.Dist.sig2=sig2;
SAout.Metafunc.Dist.phimix=phimix;

SAmeths={'PCE', 'GP', 'PC-GP'};
SAout.SAmeths=SAmeths;

%% Loop over experiments - get SA measures/ranks

% Looping through meta-experimental design, at each SA problem get SA
% measures from each method.

fparas_a=cell(Nexp,1); % cell array for storing randomly generated "a" parameters
fparas_f1=cell(Nexp,1);
fparas_f2=cell(Nexp,1);
fparas_f3=cell(Nexp,1);

S_trues=cell(Nexp,1);
ST_trues=cell(Nexp,1);
rk_trues=cell(Nexp,1); % cell arrays to store "true" rankings in for each experiment
interactions=zeros(Nexp,1);
KTtrix=zeros(Nexp,length(SAmeths));	 % this is to store the KT coeff for each method, for each experiment
KTtrix_wNaNs=KTtrix; % this is the KT matrix but also includes NaNs - to record when they happen.
Ztrix=KTtrix; %Ztrix is to store Z values in for each method and for each run
hisets=cell(Nexp,1);
hisetsizes=zeros(Nexp,1);
FracActives=zeros(Nexp,1);

PCEerror=zeros(Nexp,1);
GPerror=zeros(Nexp,1);
PCGPerror=zeros(Nexp,1);
rk_PCE=cell(Nexp,1);
rk_GP=cell(Nexp,1);
rk_PCGP=cell(Nexp,1);
STs_PCE=cell(Nexp,1);
STs_GP=cell(Nexp,1);
SThres=cell(Nexp,3);
STs_PCGP=cell(Nexp,1);
MMtimes=zeros(Nexp,3);

disp(['[#] N=',num2str(Nset),' and d=',num2str(dset)])
Xp=1;
while Xp<Nexp+1 % using a while statement here because need a way to redo iteration under certain circumstances (see below)
    disp(['[#] MetaExp No.',num2str(Xp)])    
    XsobMM=lhsdesign(Nset,dset,'iterations',100); % the last argument here is the number of iterations for the maximin LHS

    %% Build Metafunction
    Ninter2=floor(dset*inter2); % round down to nearest integer.
    Ninter3=floor(dset*inter3);
    noFXflag=1;
    while noFXflag==1 % just regenerates basis functions in case all of them are 7 (no effect), which causes an error in UQLab, amongst other things.
        para_f1=randi(9,dset,1); % these numbers dictate which basis function is associated with each Xi
        if sum((para_f1==7))<dset; noFXflag=0; end
    end
    para_f2=randi(dset,Ninter2,2); % the 2-way interactions (variable indices)
    para_f3=randi(dset,Ninter3,3); % the 3-way interactions (variable indices)
    para_a=randnmix(sig1,sig2,phimix,sum([length(para_f1),size(para_f2,1),size(para_f3,1)]),0);
    fparas_a{Xp}=para_a;
    fparas_f1{Xp}=para_f1;
    fparas_f2{Xp}=para_f2;
    fparas_f3{Xp}=para_f3;

    % bits for MCSA
    MCSAinput.modname='monsterfunc';
    MCSAinput.mpars.a=para_a;
    MCSAinput.mpars.f1=para_f1;
    MCSAinput.mpars.f2=para_f2;
    MCSAinput.mpars.f3=para_f3;
    % evaluate function
    ysobMM=monsterfunc(XsobMM,MCSAinput.mpars);
    
    %% Get true values
    % Get "true" values of ST by doing large-sample MCSA

    uqlab;
    % now have to clear variables from last time cos otherwise IOpts
    % can too many input variables to monster function
    tic
    clear IOpts MOpts myModel myInput SobolOpts
    for ii=1:dset
        IOpts.Marginals(ii).Type='Uniform' ;
        IOpts.Marginals(ii).Parameters = [0,1] ;
    end
    myInput=uq_createInput(IOpts); %#ok<NASGU>
    MOpts.mFile=MCSAinput.modname;
    MOpts.Parameters=MCSAinput.mpars;
    myModel=uq_createModel(MOpts); %#ok<NASGU>
    
    SobolOpts.Type='Sensitivity';
    SobolOpts.Method='Sobol';
    SobolOpts.Sobol.Order=1;
    SobolOpts.Sobol.SampleSize=NMCSAtrue;
    SobolAnalysis=uq_createAnalysis(SobolOpts);
    STuq=SobolAnalysis.Results.Total;
    Suq=SobolAnalysis.Results.FirstOrder;
    rk_trues{Xp}=tiedrank(-1*STuq);
    ST_trues{Xp}=STuq;
    S_trues{Xp}=Suq;
    interactions(Xp)=1-sum(Suq);
    toc

    %% Evaluate meta-methods
    input.X=XsobMM;
    input.y=ysobMM;

    %% Sparse PCE
    try
        outPCE=PCESA(input);
        STs_PCE{Xp}=outPCE.SA.Results.Total;
        MMtimes(Xp,1)=outPCE.time;
        rk_PCE{Xp}=tiedrank(-1*STs_PCE{Xp});
        KTtrix(Xp,1)=corr(rk_trues{Xp},rk_PCE{Xp},'type','Kendall');
    catch
        disp('PCE did not work for some reason. Moving on.')
        STs_PCE{Xp}=zeros(dset,1); % put in some zeros to stop errors later on.
        PCEerror(Xp)=1;
    end
    
    %% Gaussian process
    try
        outGP=GPSA_UQ(input);
        STs_GP{Xp}=outGP.SA.Results.Total;
        MMtimes(Xp,2)=outGP.time;
        rk_GP{Xp}=tiedrank(-1*STs_GP{Xp});
        KTtrix(Xp,2)=corr(rk_trues{Xp},rk_GP{Xp},'type','Kendall');
    catch
        disp('GP did not work for some reason. Moving on.')
        STs_GP{Xp}=zeros(dset,1); % put in some zeros to stop errors later on.
        GPerror(Xp)=1;
    end
    
    %% Get PC-GP
    try
        outPCGP=PCEGPSA_UQ(input);
        STs_PCGP{Xp}=outPCGP.SA.Results.Total;
        MMtimes(Xp,3)=outPCGP.time;
        rk_PCGP{Xp}=tiedrank(-1*STs_PCGP{Xp});
        KTtrix(Xp,3)=corr(rk_trues{Xp},rk_PCGP{Xp},'type','Kendall');
    catch
        disp('PC-GP did not work for some reason. Moving on.')
        STs_PCGP{Xp}=zeros(dset,1); % put in some zeros to stop errors later on.
        PCGPerror(Xp)=1;
    end
    
    %% Get performance measures

    KTtrix_wNaNs(Xp,:)=KTtrix(Xp,:); % record version possibly with NaNs in a separate array.
    KTtrix(Xp,isnan(KTtrix(Xp,:)))=0; % replace any NaNs (which represent a failure of a method, usually) with zeros, otherwise causes problems.
    
    nanflag=sum(sum(isnan(KTtrix)));
    if nanflag > 0
        disp('Nannageddon...')
        return
    end
    
    % Also get ID of most important variables. First, we need to find out which
    % are the important variables.
    
    [STsort,I]=sort(STuq,'descend'); % sort by descending ST
    STcum=cumsum(STsort/sum(STsort)); % cumulative ST
    STcum(STcum<STcut)=1; % these next two lines find the first element of STcum which is greater than STcut
    [~,hisetsize]=min(STcum-STcut); % basically the size of the set of important variables
    hiset=I(1:hisetsize); % the set of variables deemed as "active"
    hisets{Xp}=hiset;
    hisetsizes(Xp)=hisetsize;
    FracActives(Xp)=hisetsize/dset;
    
    % for PCE
    [~,STord]=sort(STs_PCE{Xp},1,'descend'); % sort measure by descending order
    SThi=STord(1:6); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
    SThres{1}=SThi;
    Ztrix(Xp,1)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
    % for GP
    [~,STord]=sort(STs_GP{Xp},1,'descend'); % sort measure by descending order
    SThi=STord(1:6); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
    SThres{2}=SThi;
    Ztrix(Xp,2)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
    % for PCGP
    [~,STord]=sort(STs_PCGP{Xp},1,'descend'); % sort measure by descending order
    SThi=STord(1:6); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
    SThres{3}=SThi;
    Ztrix(Xp,3)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
    %

    Xp=Xp+1;
end

%% write additional stuff to output
SAout.SThres=SThres;
SAout.Metafunc.para.a=fparas_a;
SAout.Metafunc.para.f1=fparas_f1;
SAout.Metafunc.para.f2=fparas_f2;
SAout.Metafunc.para.f3=fparas_f3;
SAout.Metafunc.interactions=interactions;

SAout.Results.MMtimes=MMtimes;
SAout.Results.Ranks.true=rk_trues;

SAout.Results.Ranks.hisets=hisets;
SAout.Results.Ranks.hisetsizes=hisetsizes;
SAout.Results.Ranks.FracActives=FracActives;
SAout.Results.Ranks.PCE=rk_PCE;
SAout.Results.Ranks.GP=rk_GP;
SAout.Results.Ranks.PCGP=rk_PCGP;

SAout.Results.Measures.Strue=S_trues;
SAout.Results.Measures.STtrue=ST_trues;
SAout.Results.Measures.ST_PCE=STs_PCE;
SAout.Results.Measures.ST_GP=STs_GP;
SAout.Results.Measures.ST_PCGP=STs_PCGP;

SAout.Results.KTvalues_wNaNs=KTtrix_wNaNs;
SAout.Results.PCEerror=PCEerror;
SAout.Results.GPerror=GPerror;
SAout.Results.PCGPerror=PCGPerror;

%KTtrix(KTtrix<=0)=0.001; % set any negative values to small number: this implies negative correlation which is a failure in terms of ranking variables.

SAout.Results.KTvalues=KTtrix;
SAout.Results.Zvalues=Ztrix;
