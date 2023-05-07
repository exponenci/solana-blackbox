function success = uq_test_morris_high_order_interactions(level)
% SUCCESS = UQ_TEST_MORRIS_HIGH_ORDER_INTERACTIONS(LEVEL) non-regression
%     test for the morris sensitivity method with a model that contains only 
%     fourth order interactions.
%
% See also: UQ_MORRIS_INDICES,UQ_TEST_MORRIS

%% Initialize:
uqlab('-nosplash');
rng(2*pi);

if nargin < 1
    level = 'normal';
end
fprintf(['\nRunning: |', level,...
    '| uq_test_morris_high_order_interactions...\n']);
success = 1;

% Allowed deviation from true results:
switch level
    case 'slow'
        rng('shuffle');
        Th = 0.05;
        Sensopts.Morris.FactorSamples = 1e4;
    otherwise
        Th = 0.1;
        Sensopts.Morris.FactorSamples = 1000;
end
%% Set up UQLab:
% INPUT
M = 8;
[IOpts.Marginals(1:M).Type] = deal('Uniform');
[IOpts.Marginals(1:M).Parameters] = deal([-10, 10]);
ihandle = uq_createInput(IOpts);

% MODEL
Modelopts.mFile = 'uq_high_order_interactions';
mhandle = uq_createModel(Modelopts);

% ANALYSIS
Sensopts.Type = 'Sensitivity';
Sensopts.Method = 'Morris';
Sensopts.Display = 'nothing';
[Sensopts.Factors(1:M).Boundaries] = deal([-10, 10]);

anhandle = uq_createAnalysis(Sensopts);
res = anhandle.Results(end);

%% Validate the results:
OK = false(1, 2);
% All of the indices are within 10% difference:
OK(1) = max(abs((res.MuStar - mean(res.MuStar(1)))/mean(res.MuStar))) <= Th;


% The cost is r(M + 1)
OK(2) = (res.Cost == Sensopts.Morris.FactorSamples*(M + 1));

if ~all(OK)
    error('uq_test_morris_high_order_interactions failed.');
end
    
    

