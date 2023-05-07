function Y = uq_highlynonlinear_constraint(X)


Y(:,1) = X(:,1).^2 .* X(:,2) / 20 - 1 ;

% Y(:,2) = 1 - ( a - 6 ).^2 - ( a - 6 ).^3 + 0.6 * ( a - 6 ).^4 - b ;
Y(:,2) = ( (X(:,1) + X(:,2) - 5).^2 )/30 + ...
    ( (X(:,1) - X(:,2) - 12).^2 )/120 - 1 ;

Y(:,3) = 80 ./ ( X(:,1).^2 + 8*X(:,2) + 5 ) - 1 ; 

end