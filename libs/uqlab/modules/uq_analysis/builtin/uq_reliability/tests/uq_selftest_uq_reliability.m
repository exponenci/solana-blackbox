function pass = uq_selftest_uq_reliability(level)
% PASS = UQ_SELFTEST_UQ_RELIABILITY(LEVEL):
%     Selftest for all methods implemented in the structural reliability
%     analysis module

uqlab('-nosplash');

if nargin < 1
    level = 'normal'; 
end


%% Perform tests
% Tests to perform:
TestNames = {
    'uq_Reliability_test_gradient',...
    'uq_Reliability_test_hessian',...
    'uq_Reliability_test_basic_RS',...
    'uq_Reliability_test_cubic_RS',...
    'uq_Reliability_test_lognormal',...
    'uq_Reliability_test_lognormal_correlated',...
    'uq_Reliability_test_simply_supported_beam',...
    'uq_Reliability_test_importance_sampling_ud', ...
    'uq_Reliability_test_stress_formsorm', ...
    'uq_Reliability_test_stress_mc', ...
    'uq_Reliability_test_many_outputs',...
    'uq_Reliability_test_print_and_display',...
    'uq_Reliability_test_subsetsim_mc',...
    'uq_Reliability_test_subsetsim_RS',...
    'uq_Reliability_test_subsetsim_inout',...
    'uq_Reliability_test_AKMCS_inout',...
    'uq_Reliability_test_AKMCS_RS',...
    'uq_Reliability_test_AKMCS_ED',...
    'uq_Reliability_test_SR_input_model',...
    'uq_Reliability_test_basic_RS_constant',...
    'uq_Reliability_test_cubic_RS_constant',...
    'uq_Reliability_test_subsetsim_mc_constant',...
    'uq_Reliability_test_AKMCS_RS_constant',...
    'uq_Reliability_test_APCKMCS_inout',...
    'uq_Reliability_test_APCKMCS_RS',...
    'uq_test_inverseFORM' ...
    'uq_Reliability_test_ALR_BlockComb_ED',...
    'uq_Reliability_test_ALR_inout',...
    'uq_Reliability_test_ALR_RS',...
    'uq_Reliability_test_ALR_RS_constant',...
    'uq_Reliability_test_SSER',...
    'uq_Reliability_test_SSER_multiOut'
     };

Ntests = length(TestNames);
success = false(1, Ntests);
Times = zeros(1, Ntests);
for ii = 1:Ntests
    TestTimer = tic;
    testFuncHandle = str2func(TestNames{ii});
    success(ii) = testFuncHandle(level);

    Times(ii) = toc(TestTimer);
end


%% Print out the results table and info:
Result = {'ERROR','OK'};

% Character where the result of test is displayed
ResultChar = 60; 

MinusLine(1:ResultChar+7) = deal('-');
fprintf('\n%s\n',MinusLine);
fprintf('UQ_SELFTEST_UQ_RELIABILITY RESULTS');
fprintf('\n%s\n',MinusLine);
for ii = 1:length(success)
    points(1:max(2,ResultChar-size(TestNames{ii},2))) = deal('.');
    fprintf('%s %s %s @ %g sec.\n',TestNames{ii},points,Result{success(ii)+1},Times(ii));
    clear points
end
fprintf('%s\n',MinusLine);

if all(success)
    pass = 1;
    fprintf('\n');
    fprintf(['SUCCESS: uq_reliablity module ' level ' test was successful.\n']);
else
    pass = 0;
    fprintf('\n');
    fprintf(['FAIL: uq_reliablity module ' level ' test failed.\n']);
end
fprintf('Total time: %g',sum(Times));