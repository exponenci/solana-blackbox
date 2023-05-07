function y=monsterfunc(X,PAR)

% A monster scaleable function for testing variable-dimension sensitivity
% analysis (aned maybe other things)

% Basically it uses basis functions according to vector f1, and coeffs
% according to a, and also 2 and 3-way interactions as dictated by f2 and
% f3.
%
% It also scales each output so that inputs in [0,1] map to outputs with a
% range of 1 (but not necessarily in [0,1])

[N,d]=size(X);

a=PAR.a;
f1=PAR.f1; % d-length vector composed of entries in [1,9] representing transformations below
f2=PAR.f2; % dx2 vector with 2-way interaction pairs (e.g. a row [2,3] would mean an interaction between x2 and x3
f3=PAR.f3; % same as f2 but for 3-way interactions

X1=X; % X1 will be the matrix of transformed input variables
for dd=1:d
    switch f1(dd)
        case 1 % linear
            X1(:,dd)=X(:,dd);
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
        case 2 % squared
            X1(:,dd)=X(:,dd).^2;
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
        case 3 % cubic
            X1(:,dd)=X(:,dd).^3;
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
        case 4 % exponential
            X1(:,dd)=exp(X(:,dd))/(exp(1)-1);
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
        case 5 % sin
            X1(:,dd)=sin(2*pi*X(:,dd))/2;
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
        case 6 % step
            X1(X(:,dd)<0.5,dd)=0;
            X1(X(:,dd)>=0.5,dd)=1;
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
        case 7 % switched off
            X1(:,dd)=0;
        case 8 % non-monotonic
            X1(:,dd)=4*(X(:,dd)-0.5).^2;
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
        case 9 % inverse
            X1(:,dd)=(10-1/1.1)^-1*(X(:,dd)+0.1).^-1; % added a bit here to stop very high numbers appearing for low x
            %X1(:,dd)=X1(:,dd)/range(X1(:,dd));
    end
end

y1=sum(X1.*repmat(a(1:d)',N,1),2); % sum of first order terms multiplied by coeffs. (ok)

y2=0;
for jj=1:size(f2,1)
    y2=y2+X1(:,f2(jj,1)).*X1(:,f2(jj,2))*a(jj+d); % add interaction according to f2 vector, and multiply by coeff from a
end

y3=0;
for jj=1:size(f3,1)
    y3=y3+X1(:,f3(jj,1)).*X1(:,f3(jj,2)).*X1(:,f3(jj,3))*a(jj+d+size(f2,1)); % add interaction according to f3 vector, and multiply by coeff from a
end

y=y1+y2+y3;