function [r, omega2] = ...
  red_laser(lambda0, r1_0, r2_0, N_r, alpha_0, iterations, im)

    N = N_r;                % вектор размеров эритроцитов
    
    figure()
    imshow(im);
    
    start = input('Сколько пикселей от центра до начала?    ');
    if isempty(start)
        start = 180;
    end
    finish = input('Сколько пикселей от центра до конца?     ');
    if isempty(finish)
        finish = 500;
    end
    
    start_angle = input('Начало области (угол в градусах):        ');
    if isempty(start_angle)
        start_angle = 0;
    end
    
    finish_angle = input('Конец области (угол в градусах):         ');
    if isempty(finish_angle)
        finish_angle = 359;
    end

    tic

    %%%%%% ОСНОВНЫЕ КОНФИГУРАЦИИ: %%%%%%
    r1 = r1_0;
    r2 = r2_0;
    lambda = lambda0/1000;
    r = linspace (r1, r2, N);
    
    %%%% ВОЗЬМЕМ ИНТЕНСИВНОСТЬ ИЗ ПРОГРАММЫ С ВИДНОСТЬЮ:
    
    [I0, theta0, i_min] = calc_visibility_test(im, true, true, start, finish, start_angle, finish_angle, 10);
    const_theta = i_min / 6.1;
%     % хочу подобрать коэффициенты полинома
%     % для интенсивности до первого минимума:
%     theta_test = theta0((i_min/2):i_min);
%     I_test = I0((i_min/2):i_min);
%     
%     p = polyfit(theta_test, I_test, 4);
%     theta_centr = 1 : theta0(i_min);
%     I_centr = polyval(p, theta_centr);
%     
%     theta_res = zeros(1, max(theta0));
%     I_res = zeros(1, max(theta0));
%     
%     theta_res(1:theta0(i_min)) = theta_centr;
%     theta_res(theta0(i_min)+1:max(theta0)) = theta0(i_min+1:length(theta0));
%     I_res(1:theta0(i_min)) = I_centr;
%     I_res(theta0(i_min)+1:max(theta0)) = I0(i_min+1:length(theta0));
%     
%     % нормируем данные из фотографии    
%     theta = theta_res./const_theta.*pi./180;
%     I = (I_res./max(I_res))';
    
    theta = theta0./const_theta.*pi./180;
    I = (I0)';
    
    M = length(theta);
    
    figure()
    plot(theta, I)
    xlabel('\theta, угол наблюдения');
    ylabel('I, интенсивность рассеянного света');

    % матрица K(theta[i], r[j]):
    A = zeros (M,N);
    for i = 1:M
        c = r.*2.*pi.*theta(1, i)./lambda;
        %A (i, :) = r.^4 .* (besselj(1, c)./c).^2 .* (r2-r1)./N;
        %A(i, :) = ((r .* besselj(1, c) ./ theta(1, i)).^2 .* (r2-r1)./N) .* (theta(1, i)^3) ./ (r.^2);
        A(i, :) = (r .* besselj(1, c) ./ theta(1, i)).^2 .* (r2-r1)./N;
    end
    
    %I = I .* (theta.^3)';

    %%%%% ПОДБОР НАЧАЛЬНОГО ПРИБЛИЖЕНИЯ %%%%%%
    %%%%% КВАДРАТИЧНЫМ ПРОГРАММИРОВАНИЕМ %%%%%

    E = eye (N, N);
    lb = zeros(N, 1);
    for i = 1:N
        lb(i, 1) = 0;
    end
    rb = zeros(N, 1);
    for i = 1:N
        rb(i, 1) = 1;
    end
    alpha = alpha_0;
    
    options = optimoptions(@fmincon, 'Algorithm', 'trust-region-reflective');
    % options = optimoptions(@fmincon, 'Algorithm', 'interior-point');

    H = A' * A + alpha * E;
    f = - A' * I;
    
    % зануление w_1 & w_2
%     A_eq = zeros(2, N);
%     A_eq(1, 1) = 1;
%     A_eq(2, N) = 1;
%     b_eq = zeros(2, 1);
    
    omega2 = quadprog (H, f, [], [], [], [], lb, [], [], options);
    

%      for i=1:N
%          omega2(i, 1) = 0.5;
%      end

    figure()
    plot(r, omega2)

    
    omega2 = eye(N, 1) .* 0.5;
    %%%%%% РЕШЕНИЕ ОБРАТНОЙ ЗАДАЧИ %%%%%%
    %%%%%% МЕТОДОМ ПРОЕКЦИИ ГРАДИЕНТА %%%

    E = eye (N, N);
    grad = 2.*(A'*A+alpha.*E)*omega2-2.*A'*I;
    k = 1;
    gamma = 1./max(eig(A'*A + alpha.*E));
    k_max = iterations;
    while (k < k_max) & (grad ~= zeros(N, 1))
        k = k + 1;
        omega2 = omega2-gamma.*grad;
        omega2 = max (omega2*0, omega2);
        grad = 2.*(A'*A+alpha*E)*omega2-2.*A'*I;
    end
    iter = 0;
    iter0 = k_max;
    while (iter0 >= 10)
        iter = iter + 1;
        iter0 = iter0/10;
    end

    t = toc;



    %%% ГРАФИКИ %%%
%     omega_new = omega2' ./ (r.^2);

% не баг, а фича:
omega2(r >= 5.759) = 0;

    figure()
    plot (r, omega2, 'b-') % все клетки
    xlabel('r, размер клетки');
    ylabel('\omega, плотность вероятности');
    
   
    
    % СЧИТАЕМ MEAN & STD для ЭРИТРОЦИТОВ
    w = omega2(r > 3 & r < 4.5);
    w = w(w > 0);
    x = r(omega2 > 0);
    x = x(x > 3 & x < 4.5);
    dx = (max(x) - min(x)) / length(x);
    
    square = sum(w) * dx;
    w = w ./ square;
    
    matozh = sum(x.*(w')) * dx;
    disper = sqrt(sum(x.^2.*(w')) * dx - matozh^2);

    
    figure()
    plot (x, w, 'b-')
    title ({'grad+quadprog'; ['время выполнения: ' int2str(t)]; []; ...
                ['мат.ожидание: ' num2str(matozh)]; ...
                ['дисперсия ' num2str(disper)]})
            
    xlabel('r, размер клетки');
    ylabel('\omega, плотность вероятности');
    
%     figure()
%     plot (r, omega_new, 'r')
%     title('Распределение по размерам')


   
 

end