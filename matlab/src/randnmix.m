function X=randnmix(sig1,sig2,rmix,N,plott)

% this is a function that mixes two normal distributions, the idea being to
% make something that looks sort of normal, but with tails that we can control.
%
% sig1 and sig2 are standard deviations of each normal dist. rmix is the
% ratio between the two (should be between 0 and 1). N is the number of sample points to generate.

N1=floor(rmix*N); % number of points to draw from dist 1
N2=N-N1;

X1=randn(N1,1)*sig1;
X2=randn(N2,1)*sig2;
X=[X1;X2];

if plott==1
    hist(X,floor(N/7))
end