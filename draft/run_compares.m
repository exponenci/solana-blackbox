% script runs methods comparison and receives SAout object, then plots some
% figures to represent results.

% - хотим ли мы при этом минимизировать количество значимых параметров? в 
% реализации metafunction_comparison не показывается количество
% значимых параметров для каждого отдельного метода анализа. хотим ли мы
% знать количество активных параметров (для какого-то STcut)?
% - для Solana, по-моему, разумно выставить размерность (d) U[85,95]
% - для указанных размерностей количество Run-ов (N) должно быть выставлено
% хотя бы в 5 раз больше (это видно по fig.8 из статьи, этот график 
% без значения среднего воспроизводит 4я секция этого скрипта; для методов 
% SM и MJ это может быть критично)
% - из прочего: как сэмплить модель можно указать с помощью флага metasamp;
% можно выбрать то, как выбираются значения Omega (миксом двух нормальных
% распределений или экспоненциальным)

exp_count = 1;
SAout = metafunction_comparison(exp_count);

dimensions = SAout.MetaExp.Xmeta(:, 2); % experiments dimensions (d-values)

%% Z* value colorbar
% значение показывает долю угаданных значимых признаков

figure('Name', 'Z* values');
for index = 1:6
    subplot(3, 2, index);
    nruns = SAout.Results.NrunsAll(:, index);
    zvalues = SAout.Results.Zvalues(:, index);
    scatter(nruns,dimensions,[],zvalues,'filled');
    colorbar;
    %xlim([80 300]);
    %ylim([80 100]);
    caxis([0, 1]);
    xlabel('N');
    ylabel('d');
    title(SAout.SAmeths(index));
end
colormap summer;

%% tau value colorbar
% значение показывает, насколько хорошо метод выставил ранги параметров

figure('Name', 'Tau values');
for index = 1:6
    subplot(3, 2, index);
    nruns = SAout.Results.NrunsAll(:, index);
    tau_values = SAout.Results.KTvalues(:, index);
    scatter(nruns,dimensions,[],tau_values,'filled');
    colorbar;
    %xlim([80 300]);
    %ylim([80 100]);
    caxis([-1, 1]);
    xlabel('N');
    ylabel('d');
    title(SAout.SAmeths(index));
end
colormap summer;

%% mean tau and Z* values

figure('Name', 'Mean values');
mean_tau = [0, 0, 0, 0, 0, 0];
mean_z = [0, 0, 0, 0, 0, 0];
%for index = 1:6
for index = 1:3
    mean_tau(index) = mean(SAout.Results.KTvalues(:, index));
    mean_z(index) = mean(SAout.Results.Zvalues(:, index));
end

% bar plot for tau
subplot(1, 2, 1);
bar(mean_tau);
ylim([0 1]);
title("Mean tau values per method");
set(gca, 'xticklabel', SAout.SAmeths);

% bar plot for Z*
subplot(1, 2, 2);
bar(mean_z);
ylim([0 1]);
title("Mean Z* values per method");
set(gca, 'xticklabel', SAout.SAmeths);

%% N/d relation impact
% to get some usefull info from this plot, a lot of experimetns must be ran
figure('Name', 'Z* against N/d');
n_exp = SAout.MetaExp.Nexp;
for index = 1:6
    subplot(3, 2, index);
    relation = SAout.Results.NrunsAll(:, index)./dimensions;
    zvalues = SAout.Results.Zvalues(:, index);
    scatter(relation, zvalues, [], 'black', 'filled');
    ylim([0 1]);
    xlabel('N/d');
    ylabel('Z*');
    title(SAout.SAmeths(index));
end
