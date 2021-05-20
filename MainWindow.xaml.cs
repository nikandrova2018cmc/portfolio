using System;
using System.Windows;
using System.Text;
using System.Windows.Controls;
using System.ComponentModel;
using System.Collections.ObjectModel;
using MathWorks.MATLAB.NET.Utility;
using MathWorks.MATLAB.NET.Arrays;
using System.Diagnostics;
using ln_grad;
using ln_quadprog;
using ln_lsqlin;

namespace Laser
{
    /// <summary>
    /// Логика взаимодействия для MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window, INotifyPropertyChanged
    {

        public event PropertyChangedEventHandler PropertyChanged; // Событие, которое нужно вызывать при изменении

        // Для удобства обернем событие в метод с единственным параметром - имя изменяемого свойства
        public void RaisePropertyChanged(string propertyName)
        {
            // Если кто-то на него подписан, то вызывем его
            if (PropertyChanged != null)
                PropertyChanged(this, new PropertyChangedEventArgs(propertyName));
        }
        public MainWindow()
        {
            InitializeComponent();
            DataContext = this;
            N = 100;
            M = 100;
            Lambda = 633;
            R1 = 2;
            R2 = 6;
            Theta = 15;
            Noise = 1;
            Iteration = 10000;
        }

        /*class Methods : ObservableCollection<string>
        {
            public Methods()
            {
                Add("Метод проекции градиента");
                Add("Метод квадратичного программирования");
                Add("Метод наименьших квадратов");
            }
        }*/

        double lambda_0, r1_0, r2_0, n_0, m_0, theta_0, noise_0, iteration_0;
        string selectedMethod = "Метод проекции градиента";

        MWArray[] res = null; //выходной массив метода plane
        MWNumericArray descriptor = null; //массив возвращаемого параметра 

        public double N
        {
            get { return n_0; }
            set
            {  // Устанавливаем новое значение
                n_0 = value;
                // Сообщаем всем, кто подписан на событие PropertyChanged, что поле изменилось Name
                RaisePropertyChanged("N");
            }
        }

        public double Lambda
        {
            get { return lambda_0; }
            set
            { 
                lambda_0 = value;
                RaisePropertyChanged("Lambda");
            }
        }

        public double R1
        {
            get { return r1_0; }
            set
            {
                r1_0 = value;
                RaisePropertyChanged("R1");
            }
        }

        public double R2
        {
            get { return r2_0; }
            set
            {
                r2_0 = value;
                RaisePropertyChanged("R2");
            }
        }

        public double Theta
        {
            get { return theta_0; }
            set
            {
                theta_0 = value;
                RaisePropertyChanged("Theta");
            }
        }

        private void methods_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {

        }

        public double M
        {
            get { return m_0; }
            set
            {
                m_0 = value;
                RaisePropertyChanged("M");
            }
        }

        public double Noise
        {
            get { return noise_0; }
            set
            {
                noise_0 = value;
                RaisePropertyChanged("Noise");
            }
        }

        public double Iteration
        {
            get { return iteration_0; }
            set
            {
                iteration_0 = value;
                RaisePropertyChanged("Iteration");
            }
        }

        public string Methods
        {
            get { return selectedMethod; }
            set
            {
                selectedMethod = value;
                RaisePropertyChanged("Methods");
            }
        }

        private void Start_Click(object sender, EventArgs e)
        {
            try
            {
                //MWCharArray mw_func = new MWCharArray(func);//преобразование строки функции в тип MWCharArray
                n_0 = Convert.ToDouble(n.Text); //преобразоване string в double
                m_0 = Convert.ToDouble(m.Text);
                lambda_0 = Convert.ToDouble(lambda.Text);
                r1_0 = Convert.ToDouble(r1.Text);
                r2_0 = Convert.ToDouble(r2.Text);
                theta_0 = Convert.ToDouble(theta.Text);
                noise_0 = Convert.ToDouble(noise.Text);
                iteration_0 = Convert.ToDouble(iteration.Text);
                selectedMethod = methods.Text;


                if (selectedMethod == "Метод проекции градиента")
                {
                    ln_grad.Class1 obj_grad = new ln_grad.Class1(); //экземпляр класса компонента
                    res = obj_grad.ln_grad(2, lambda_0, r1_0, r2_0, n_0, m_0, theta_0, noise_0, iteration_0);
                }
                if (selectedMethod == "Метод квадратичного программирования")
                {
                    ln_quadprog.Class2 obj_quadprog = new ln_quadprog.Class2(); //экземпляр класса компонента
                    res = obj_quadprog.ln_quadprog(2, lambda_0, r1_0, r2_0, n_0, m_0, theta_0, noise_0);
                }
                if (selectedMethod == "Метод наименьших квадратов")
                {
                    ln_lsqlin.Class3 obj_lsqlin = new ln_lsqlin.Class3(); //экземпляр класса компонента
                    res = obj_lsqlin.ln_lsqlin(2, lambda_0, r1_0, r2_0, n_0, m_0, theta_0, noise_0);
                }


                descriptor = (MWNumericArray)res[0]; //выбор первого элемента из массива MWArray и преобразование в числовой тип MWNumericArray
                double[,] d_descriptor = (double[,])descriptor.ToArray(MWArrayComponent.Real);//преобразование массива MWNUmericArray  к масииву типа double  

                //for (int i = 0; i < d_descriptor.Length; i++)//вывод массива d_descriptor в RichBox
                //{
                //    richTextBox1.Text += i.ToString() + '\t';
                //    richTextBox1.Text += d_descriptor[i, 0].ToString("0.000") + '\n';//преобразование элеметна массива double в string
                //}
            }
            catch (Exception ex)//обработка исключения 
            {
                System.Windows.Forms.MessageBox.Show(ex.Message);
            }
        }

        private void Clear_Click(object sender, EventArgs e)
        {
            res = null;//обнуление массивов
            descriptor = null;
        }

        private void Default_Click(object sender, EventArgs e)
        {
            n.Text = "100";
            m.Text = "100";
            lambda.Text = "633";
            r1.Text = "2";
            r2.Text = "6";
            theta.Text = "15";
            noise.Text = "1";
            iteration.Text = "10000";
            res = null;//обнуление массивов
            descriptor = null;
        }

       /* private void methods_SelectionChanged(object sender, EventArgs e)
        {
            //ComboBoxItem cbi = ((sender as ComboBox).SelectedItem as ComboBoxItem);
            //selectedMethod = cbi.Content.ToString();
            ComboBox cb = sender as ComboBox;
            selectedMethod = cb.Text;
        }*/
    }
}
