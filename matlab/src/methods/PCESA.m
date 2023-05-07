function out=PCESA(input)

% This is a function that takes some input/output data and performs a
% sensitivity analysis  using the PCE through UQLab. This function is
% basically to take default options and make it easy for me to run SA
% through UQLab. Obviously plenty more options and detail available in
% UQLab itself.
%
% If you want UQLab to control sampling, you need to specify:
% .mFile - the filename of the model
% .par   - model parameters (as a vector or structure), if needed
% .Nsamp - number of sample points to use
% .k     - number of input variables
%
% If you want to use own sample, you need to specify:
% .X     - the input matrix
% .y     - the output vector

% Assumes uniform distributions over [0,1]

% So far, just needs X and y as inputs (input.X and input.y). Obviously
% could extend this a lot.

tstart=tic;
uqlab;
% Create a MODEL object from the function file:
usersamp=0;
try
    ModelOpts.mFile = input.mFile; % the file name of the model
    ModelOpts.Parameters = input.par; % the parameters of the model
    myModel = uq_createModel(ModelOpts);
    Nsamp=input.Nsamp;
    k=input.k;
catch
    X=input.X;
    y=input.y;
    k=size(X,2);
    usersamp=1;
end

% define input dists as 0,1 uniform
for ii=1:k
    IOpts.Marginals(ii).Type = 'Uniform' ;
    IOpts.Marginals(ii).Parameters = [0,1] ;
end
myInput = uq_createInput(IOpts); %#ok<NASGU> % this stores the input info in UQlab (doesn't need to be called again directly)

PCEOpts.Type='Metamodel';
PCEOpts.MetaType='PCE';
PCEOpts.Method = 'LARS';
PCEOpts.TruncOptions.qNorm = 0.75;
PCEOpts.TruncOptions.MaxInteraction=2;
PCEOpts.Degree=1:5;

if usersamp==1
    PCEOpts.ExpDesign.Sampling='User';
    PCEOpts.ExpDesign.X=X;
    PCEOpts.ExpDesign.Y=y;
else
    PCEOpts.FullModel = myModel;
    PCEOpts.ExpDesign.NSamples = Nsamp;
    PCEOpts.ExpDesign.Sampling = 'LHS';
end
PCEModel = uq_createModel(PCEOpts);

PCESobol.Type = 'Sensitivity';
PCESobol.Method = 'Sobol';
PCESobol.Sobol.Order = 1; % as far as I know, this should not affect the values of ST
SA=uq_createAnalysis(PCESobol);

out.PCEModel=PCEModel;
out.SA=SA;
out.time=toc(tstart);