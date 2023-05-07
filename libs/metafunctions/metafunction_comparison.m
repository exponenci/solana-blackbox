function SAout=metafunction_comparison(Nexp,basehold)

% This is a partially complete demo of the scripts used to generate resuts
% in the paper "Metafunctions for benchmarking in sensitivity analysis", by
% William Becker (Reliability Engineering and System Safety).
%
% It generates sensitivity analysis experiments using the "metafunction"
% approach, and compares various sensitivity analysis methods on this
% basis. Here, 6 methods are compared which are available in UQLab, and one
% that is coded here into the script (Lamboni estimator).
%
% Nexp is the number of SA experiments to run
% basehold should be set to a value between 0 and 9. 0 retains all basis
% functions of the metafunction, otherwis a value i holds out the ith function
%
% For this to work, you will need to have UQLab installed, the Stats and
% Machine Learning Toolbox, and the Optimization toolbox (at least).
%
% Please note, this is not intended for general distribution, in that the
% code was not specifically written for public release. It may not be clear
% in all places, and might not necessary work on future Matlab versions. 
% However, it should all work. It is available in the
% interests of transparency and reproducibility.
%
% See the paper for more details, or contact me on
% william.becker@bluefoxdata.eu

tic

MetaOff=0; % set to 1 to turn GPs off (faster, and also if opt toolbox not available)

% Concerning number of model runs
Nlow=10;
Nhigh=100;

SAout.MetaExp.Nlow=Nlow;
SAout.MetaExp.Nhigh=Nhigh;

% Concerning dimensionality
dlow=2;
dhigh=5;

SAout.MetaExp.dlow=dlow;
SAout.MetaExp.dhigh=dhigh;

% Other general settings
NMCSAtrue=10000; % the number of (k+1) designs to use in estimation of "true" ST values.
STcut=0.95; % this is a parameter to control how many variables to count as "important". Basically the fraction of the sum of ST which we want to keep in.
metasamp=2; % set to 1 if use Sobol' sampling for metamodel design, or 2 to use maximin LHS

SAout.MetaExp.Nexp=Nexp;
SAout.MetaExp.NMCSAtrue=NMCSAtrue;

%%% Metafunction settings
inter2=0.5; % fraction (of d) of 2 way interactions (e.g. if d=10 and inter2=0.5, there will be 5 2-way interaction terms
inter3=0.2; % same for 3 way.
% the following are parameters for the randnmix function, mixture of two
% normal dists.
sig1=0.5;
sig2=5;
phimix=0.7;

SAout.Metafunc.Dist.d2=inter2;
SAout.Metafunc.Dist.d3=inter3;
SAout.Metafunc.Dist.sig1=sig1;
SAout.Metafunc.Dist.sig2=sig2;
SAout.Metafunc.Dist.phimix=phimix;
SAout.Metafunc.Dist.basehold=basehold;

%% Meta Experimental Design

% Pre-generate meta-experimental design, i.e. a series of SA problems each
% with an N, a k, and parameters of function

%Xmeta=net(sobolset(2,'Skip',1),Nexp); % this is the set of experiments to run - N and d values
Xmeta=rand(Nexp,2);
Xmeta=[Xmeta(:,1)*(Nhigh-Nlow)+Nlow,Xmeta(:,2)*(dhigh-dlow)+dlow];
Xmeta=floor(Xmeta);

SAmeths={'SM','MJ','LAM','PCE','GP','PC-GP'};
SAmeths_long={'Sobol-Mauntz','Monod-Janon','Lamboni',...
    'Sparse polynomial chaos expansion','Gaussian process',...
    'Polynomial chaos Gaussian process'};
if MetaOff==1
    SAmeths(4:end)=[];
    SAmeths_long(4:end)=[];
end
SAout.SAmeths=SAmeths;
SAout.SAmeths_long=SAmeths_long;
%% Loop over experiments - get SA measures/ranks

% Looping through meta-experimental design, at each SA problem get SA
% measures from each method.

fparas_a=cell(Nexp,1); % cell array for storing randomly generated "a" parameters
fparas_f1=cell(Nexp,1);
fparas_f2=cell(Nexp,1);
fparas_f3=cell(Nexp,1);
ST_trues=cell(Nexp,1);
S_trues=cell(Nexp,1);
STs_SM=cell(Nexp,1);
STs_MJ=cell(Nexp,1);
STs_LAM=cell(Nexp,1);

rk_trues=cell(Nexp,1); % cell arrays to store "true" rankings in for each experiment
rk_SM=cell(Nexp,1);
rk_MJ=cell(Nexp,1);
rk_LAM=cell(Nexp,1);

if MetaOff==0; STs_PCE=cell(Nexp,1); rk_PCE=cell(Nexp,1); rk_GP=cell(Nexp,1); STs_GP=cell(Nexp,1);... 
        rk_PCGP=cell(Nexp,1); STs_PCGP=cell(Nexp,1); MMtimes=zeros(Nexp,3); end

KTtrix=zeros(Nexp,length(SAmeths));	 % this is to store the KT coeff for each method, for each experiment
KTtrix_wNaNs=KTtrix; % this is the KT matrix but also includes NaNs - to record when they happen.
Ztrix=KTtrix; %Ztrix is to store Z values in for each method and for each run
NexpMCSA=zeros(Nexp,1); % vector for storing actual sample sizes used in most methods
NexpLAM=zeros(Nexp,1); % the actual number of runs used for Lamboni (since it is a d+2 multiple). Should be the same as VARS I think.
hisets=cell(Nexp,1);
hisetsizes=zeros(Nexp,1);
FracActives=zeros(Nexp,1);
interactions=zeros(Nexp,1);
GPerror=zeros(Nexp,1);
PCEerror=zeros(Nexp,1);
PCGPerror=zeros(Nexp,1);
NrunsAll=zeros(Nexp,length(SAmeths));

Xp=1;
while Xp<Nexp+1 % using a while statement here because need a way to redo iteration under certain circumstances (see below)
    while Xmeta(Xp,1)/(Xmeta(Xp,2)+1)<1 % if less than one (k+1) design
        Xmeta(Xp,:)=rand(1,2); % generate new values
        Xmeta(Xp,:)=[Xmeta(Xp,1)*(Nhigh-Nlow)+Nlow,Xmeta(Xp,2)*(dhigh-dlow)+dlow];
        Xmeta(Xp,:)=floor(Xmeta(Xp,:));
    end
    NN=Xmeta(Xp,1); % the sample size for this experiment
    dd=Xmeta(Xp,2); % the dimensionality for this experiment
    NexpMCSA(Xp)=floor(NN/(dd+1))*(dd+1); % this is the actual number of points used for each of the MCSA experiments - NN rounded down to the nearest (d+1) multiple
    disp(['MetaExp No.',num2str(Xp),' (N=',num2str(NexpMCSA(Xp)),' and d=',num2str(dd),').'])
    
    if metasamp==1
        XsobMM=net(sobolset(dd,'Skip',1),NexpMCSA(Xp));
    elseif metasamp==2
        XsobMM=lhsdesign(NexpMCSA(Xp),dd,'iterations',100); % the last argument here is the number of iterations for the maximin LHS
    end
    
    %% Build Metafunction
    
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
    %             para_a=exprnd(1,sum([length(para_f1),size(para_f2,1),size(para_f3,1)]),1); % exponentially distrubuted coefficients
    %             negs=randi(2,length(para_a),1);
    %             negs(negs==2)=-1;
    %             para_a=para_a.*negs; % now laplace distributed coeffs
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
    % evaluate function for non-MCSA methods
    ysobMM=monsterfunc(XsobMM,MCSAinput.mpars);
    
    % Get "true" values of ST by doing large-sample MCSA
    
    uqlab;
    % now have to clear variables from last time cos otherwise IOpts
    % can too many input variables to monster function
    clear IOpts MOpts myModel myInput SobolOpts
    for ii=1:dd
        IOpts.Marginals(ii).Type = 'Uniform' ;
        IOpts.Marginals(ii).Parameters = [0,1] ;
    end
    myInput = uq_createInput(IOpts); %#ok<NASGU>
    MOpts.mFile = MCSAinput.modname;
    MOpts.Parameters=MCSAinput.mpars;
    myModel = uq_createModel(MOpts); %#ok<NASGU>
    
    SobolOpts.Type = 'Sensitivity';
    SobolOpts.Method = 'Sobol';
    SobolOpts.Sobol.Order = 1;
    SobolOpts.Sobol.SampleSize = NMCSAtrue;
    SobolAnalysis = uq_createAnalysis(SobolOpts);
    STuq=SobolAnalysis.Results.Total;
    Suq=SobolAnalysis.Results.FirstOrder;
    rk_trues{Xp}=tiedrank(-1*STuq);
    ST_trues{Xp}=STuq;
    S_trues{Xp}=Suq;
    interactions(Xp)=1-sum(Suq);
    
    
    %% Get Monod-Janon
    NMCSA=NexpMCSA(Xp)/(dd+1);
    try
        SobolOpts.Sobol.SampleSize = NMCSA;
        SobolOpts.Sobol.Estimator = 'janon';
        SobolAnalysis = uq_createAnalysis(SobolOpts);
        STs_MJ{Xp}=SobolAnalysis.Results.Total;
    catch
        warning('Couldnt get Janon Monte Carlo ST via UQLab - probably too few sample points')
        STs_MJ{Xp}=zeros(dd,1);
    end
    
    NrunsAll(Xp,2)=NMCSA*(dd+1); % this is different from the .cost output of UQlab, because that also includes cost of estimating Si.
    
    %% Get Sobol-Mauntz
    try
        SobolOpts.Sobol.SampleSize = NMCSA;
        SobolOpts.Sobol.Estimator = 'sobol';
        SobolAnalysis = uq_createAnalysis(SobolOpts);
        STs_SM{Xp}=SobolAnalysis.Results.Total;
    catch
        warning('Couldnt get Sobol Monte Carlo ST via UQLab - probably too few sample points')
        STs_SM{Xp}=zeros(dd,1);
    end
    
    NrunsAll(Xp,1)=NMCSA*(dd+1);
    
    %% Get Lamboni with p=3
    
    par=MCSAinput.mpars; % for conciseness
    
    NLam=floor(NN/(2*dd+1)); % round down to the nearest multiple of d+2: this should be the cost of Lamboni with p=3
    %NexpLAM(Xp)=NLam*(dd+2);
    
    Xsob=rand(NLam,dd*3); % Using pure random sampling as per other methods
    A=Xsob(:,1:dd);
    B=Xsob(:,dd+1:2*dd);
    C=Xsob(:,2*dd+1:3*dd);
    
    % run A through model to get YA
    YA=monsterfunc(A,par);
    NrunsLAM=length(YA);
    if NrunsLAM<=1
        varY=1;
    elseif NrunsLAM>1
        varY=var(YA); % only allowed to use YA I think. Not that it matters because I am only ranking here.
    end
    
    %looping over inputs
    VT=zeros(dd,1);
    for zz=1:dd
        ABi=A;
        ABi(:,zz)=B(:,zz); % subst column
        ACi=A;
        ACi(:,zz)=C(:,zz); % subst column
        
        % run ABi and ACi through model to get YABi and YACi
        YABi=monsterfunc(ABi,par);
        YACi=monsterfunc(ACi,par);
        NrunsLAM=NrunsLAM+length(YABi)+length(YACi); % explicit run counter
        
        % make the terms in the sum 3.21
        S1=(YA-0.5*YABi-0.5*YACi).^2;
        S2=(YABi-0.5*YA-0.5*YACi).^2;
        S3=(YACi-0.5*YA-0.5*YABi).^2;
        
        % put it all together
        VT(zz)=(2/(9*NLam))*(sum(S1)+sum(S2)+sum(S3));
    end
    
    STs_LAM{Xp}=VT/varY; % get STs
    NrunsAll(Xp,3)=NrunsLAM;
    NexpLAM(Xp)=NrunsLAM;
    
    if MetaOff==0 % In here we have the emulators which are much slower
        
        %% Sparse PCE
        input.X=XsobMM;
        input.y=ysobMM;
        NrunsAll(Xp,4)=length(input.y);
        NrunsAll(Xp,5)=length(input.y);
        NrunsAll(Xp,6)=length(input.y);
        %input.Nsamp=
        try
            outPCE=PCESA(input);
            STs_PCE{Xp}=outPCE.SA.Results.Total;
            MMtimes(Xp,1)=outPCE.time;
            rk_PCE{Xp}=tiedrank(-1*STs_PCE{Xp});
            KTtrix(Xp,4)=corr(rk_trues{Xp},rk_PCE{Xp},'type','Kendall');
        catch
            disp('PCE did not work for some reason. Moving on.')
            STs_PCE{Xp}=zeros(dd,1); % put in some zeros to stop errors later on.
            PCEerror(Xp)=1;
        end
        
        %% Gaussian process
        try
            outGP=GPSA_UQ(input);
            STs_GP{Xp}=outGP.SA.Results.Total;
            MMtimes(Xp,2)=outGP.time;
            rk_GP{Xp}=tiedrank(-1*STs_GP{Xp});
            KTtrix(Xp,5)=corr(rk_trues{Xp},rk_GP{Xp},'type','Kendall');
        catch
            disp('GP did not work for some reason. Moving on.')
            STs_GP{Xp}=zeros(dd,1); % put in some zeros to stop errors later on.
            GPerror(Xp)=1;
        end
        
        %% Get PC-GP
        try
            outPCGP=PCEGPSA_UQ(input);
            STs_PCGP{Xp}=outPCGP.SA.Results.Total;
            MMtimes(Xp,3)=outPCGP.time;
            rk_PCGP{Xp}=tiedrank(-1*STs_PCGP{Xp});
            KTtrix(Xp,6)=corr(rk_trues{Xp},rk_PCGP{Xp},'type','Kendall');
        catch
            disp('PC-GP did not work for some reason. Moving on.')
            STs_PCGP{Xp}=zeros(dd,1); % put in some zeros to stop errors later on.
            PCGPerror(Xp)=1;
        end
    end
    
    %% Get performance measures
    
    % Get ranks from each method
    rk_SM{Xp}=tiedrank(-1*STs_SM{Xp});   
    rk_MJ{Xp}=tiedrank(-1*STs_MJ{Xp});   
    rk_LAM{Xp}=tiedrank(-1*STs_LAM{Xp});

    
    % Kendall-tau correlation of estimated ranks with "true" ranks using
    % large sample size
    KTtrix(Xp,1)=corr(rk_trues{Xp},rk_SM{Xp},'type','Kendall');
    KTtrix(Xp,2)=corr(rk_trues{Xp},rk_MJ{Xp},'type','Kendall'); 
    KTtrix(Xp,3)=corr(rk_trues{Xp},rk_LAM{Xp},'type','Kendall');
    
    KTtrix_wNaNs(Xp,:)=KTtrix(Xp,:); % record version possibly with NaNs in a separate array.
    KTtrix(Xp,isnan(KTtrix(Xp,:)))=0; % replace any NaNs (which represent a failure of a method, usually) with zeros, otherwise causes problems.
    
    nanflag=sum(sum(isnan(KTtrix)));
    if nanflag>0
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
    FracActives(Xp)=hisetsize/dd;
    
    [~,STord]=sort(STs_SM{Xp},1,'descend'); % sort measure by descending order
    SThi=STord(1:hisetsize); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
    Ztrix(Xp,1)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
    %
    [~,STord]=sort(STs_MJ{Xp},1,'descend'); % sort measure by descending order
    SThi=STord(1:hisetsize); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
    Ztrix(Xp,2)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
    %
    [~,STord]=sort(STs_LAM{Xp},1,'descend'); % sort measure by descending order
    SThi=STord(1:hisetsize); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
    Ztrix(Xp,3)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.

    if MetaOff==0
        %
        [~,STord]=sort(STs_PCE{Xp},1,'descend'); % sort measure by descending order
        SThi=STord(1:hisetsize); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
        Ztrix(Xp,4)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
        %        
        [~,STord]=sort(STs_GP{Xp},1,'descend'); % sort measure by descending order
        SThi=STord(1:hisetsize); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
        Ztrix(Xp,5)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
        %
        [~,STord]=sort(STs_PCGP{Xp},1,'descend'); % sort measure by descending order
        SThi=STord(1:hisetsize); % knowing hisetsize, the number of significant variables (defined above), take the hisetsize highest ranking variables
        Ztrix(Xp,6)=1-length(setdiff(hiset,SThi))/length(hiset); % count fraction of significant variables included in top variables.
    end
    %
    
    Xp=Xp+1;
    
end

%% write additional stuff to output

SAout.MetaExp.Xmeta=Xmeta;

SAout.Metafunc.para.a=fparas_a;
SAout.Metafunc.para.f1=fparas_f1;
SAout.Metafunc.para.f2=fparas_f2;
SAout.Metafunc.para.f3=fparas_f3;
SAout.Metafunc.interactions=interactions;

if MetaOff==0
    SAout.Results.MMtimes=MMtimes;
end
SAout.Results.Ranks.true=rk_trues;

SAout.Results.Ranks.SM=rk_SM;
SAout.Results.Ranks.MJ=rk_MJ;
SAout.Results.Ranks.LAM=rk_LAM;

SAout.Results.Ranks.hisets=hisets;
SAout.Results.Ranks.hisetsizes=hisetsizes;
SAout.Results.Ranks.FracActives=FracActives;

SAout.Results.Measures.STtrue=ST_trues;
SAout.Results.Measures.Strue=S_trues;
SAout.Results.Measures.ST_SM=STs_SM;
SAout.Results.Measures.ST_MJ=STs_MJ;
SAout.Results.Measures.ST_LAM=STs_LAM;

if MetaOff==0
    SAout.Results.Ranks.PCE=rk_PCE;
    SAout.Results.Measures.ST_PCE=STs_PCE;
    SAout.Results.Ranks.GP=rk_GP;
    SAout.Results.Measures.ST_GP=STs_GP;
    SAout.Results.Ranks.PCGP=rk_PCGP;
    SAout.Results.Measures.ST_PCGP=STs_PCGP;
end

SAout.Results.NrunsAll=NrunsAll;
SAout.Results.NexpMCSA=NexpMCSA;
SAout.Results.NexpLAM=NexpLAM;
SAout.Results.KTvalues_wNaNs=KTtrix_wNaNs;
SAout.Results.GPerror=GPerror;
SAout.Results.PCEerror=PCEerror;
SAout.Results.PCGPerror=PCGPerror;

%KTtrix(KTtrix<=0)=0.001; % set any negative values to small number: this implies negative correlation which is a failure in terms of ranking variables.

SAout.Results.KTvalues=KTtrix;
SAout.Results.Zvalues=Ztrix;

toc