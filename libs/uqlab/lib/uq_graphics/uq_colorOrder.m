function colors = uq_colorOrder( N )
%UQ_COLORORDER returns a set of RGB colors for plots.
%
%   This is the standard color scheme for plots created by UQLab.

%% Define the color order(s)
UQChairColors = [...
    0,  0,  205 ;...
    34, 139,34  ;...
    255,127,0   ;...
    205, 16,118 ;...
    238,  0,0   ;...
    186, 85,211 ]/255;
% 30/04/19: taking orange as second color
alt1 = [...
    0,  0,  205 ;...
    255,127,0   ;...
    34, 139,34  ;...
    205, 16,118 ;...
    238,  0,0   ;...
    186, 85,211 ]/255;
% 30/04/19: new proposal
alt2 = [...
    0,      76,     153 ;...
    240,    135,    0   ;...
    34,     139,    34  ;...
    237,    177,    34  ;...
    186,    85,     211 ;...
    0,      204,    204 ;...
    204,    0,     	0   ]/255;

%% Assign the color order
colorOrder = alt2;
defaultlength = size(colorOrder,1);

% Give all Chair colors if no number is specified
if ~exist('N','var')
    N = defaultlength;
end
if N <= defaultlength
    colors = colorOrder(1:N,:);
else
    colors = zeros(N,3);
    colors(:,1) = interp1(linspace(0,1,size(colorOrder,1)), colorOrder(:,1), linspace(0,1,N));
    colors(:,2) = interp1(linspace(0,1,size(colorOrder,1)), colorOrder(:,2), linspace(0,1,N));
    colors(:,3) = interp1(linspace(0,1,size(colorOrder,1)), colorOrder(:,3), linspace(0,1,N));
end

end
