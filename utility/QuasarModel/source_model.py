import numpy as np
from numpy import log, where, exp
from utility.QuasarModel.gauss import Gaussian, GaussList
import scipy


class SourceModel:
    stop: bool = False

    def process(self, x_l, y_l, intensity_l):
        """
        Model a quasar image with gaussian functions.
        :param image: np.array of image data
        :return: org - original input image, mdl - modelled image, anl - analytical fourier transform of modelled image
        """

        gauss_fnd = GaussList()

        for index in range(10):
            if self.stop:
                break

            peaks = peak_local_max(x_l, y_l, intensity_l, threshold_abs=max(intensity_l)*0.1, num_peaks=10)
            num_peaks = len(peaks)
            if num_peaks == 0:
                break

            gauss_now = GaussList()

            for i in range(num_peaks):
                gauss_now.append(self.initial_guess(peaks[i]))
            chi_sq_dof = self.find_chi_sq_dof(x_l, y_l, intensity_l, gauss_now)
            chi_sq_dof_old = chi_sq_dof

            gauss_now, chi_sq_dof, step_min = self.least_sq_gauss(gauss_now, x_l, y_l, intensity_l)
            delta_chi = chi_sq_dof_old - chi_sq_dof
            chi_sq_dof_old = chi_sq_dof

            print("-------------------")
            print("Iteration:",index)
            print("a:", gauss_now[0].a)
            print("b:", gauss_now[0].b)
            print("x0:", gauss_now[0].x0)
            print("y0:", gauss_now[0].y0)
            print("amp:", gauss_now[0].amp)
            print("theta:", gauss_now[0].theta)

            for iteration in range(2, 12):
                if self.stop:
                    break

                if step_min == 0 or abs(delta_chi) < 10 ** (-8) or iteration == 11:
                    gauss_fnd.append(gauss_now)

                    intensity_comp = list(map(lambda x,y: gauss_fnd.get_gauss(x,y), x_l, y_l))
                    intensity_l = list(map(lambda i,ic: i-ic, intensity_l, intensity_comp))
                    break
                else:
                    gauss_now, chi_sq_dof, step_min = self.least_sq_gauss(gauss_now, x_l, y_l, intensity_l)
                    delta_chi = chi_sq_dof_old - chi_sq_dof
                    chi_sq_dof_old = chi_sq_dof
            
                print("-------------------")
                print("Iteration:",index)
                print("a:", gauss_now[0].a)
                print("b:", gauss_now[0].b)
                print("x0:", gauss_now[0].x0)
                print("y0:", gauss_now[0].y0)
                print("amp:", gauss_now[0].amp)
                print("theta:", gauss_now[0].theta)


        return gauss_fnd

    def least_sq_gauss(self, gauss_now, x_l, y_l, intensity_l):

        delta_gauss = self.compute_adjustment(gauss_now, x_l, y_l, intensity_l)
        chi_from_step = []
        steps = [0, 0.6, 1.2]  # Three points which a parabola is fitted through

        for step in steps:
            chi_from_step.append(self.find_chi_sq_dof(x_l, y_l, intensity_l, gauss_now.add(delta_gauss, step)))

        chi_sq_dof_one, chi_sq_dof_two, chi_sq_dof_three = chi_from_step
        step_one, step_two, step_three = steps

        """
        For a parabola on the form: f(x) = a*x^2 + b*x + c, fitted through three points, a and b can be calculated with 
        the following formulas.
        """
        a = (step_three * (chi_sq_dof_two - chi_sq_dof_one) + step_two * (
                chi_sq_dof_one - chi_sq_dof_three) + step_one * (chi_sq_dof_three - chi_sq_dof_two)) / (
                    (step_one - step_two) * (step_one - step_three) * (step_two - step_three))
        b = (step_one ** 2 * (chi_sq_dof_two - chi_sq_dof_three) + step_three ** 2 * (
                chi_sq_dof_one - chi_sq_dof_two) + step_two ** 2 * (
                     chi_sq_dof_three - chi_sq_dof_one)) / ((step_one - step_two) * (step_one - step_three) * (
                step_two - step_three))

        step_min = np.divide(- b, (2 * a))  # The extreme (minimum value) of a parabola is situated in this point
               
        if step_min > 2:
            step_min = 2
        elif step_min < -1:
            step_min = -1

        gauss_min_chi = gauss_now.add(delta_gauss, step_min)
        chi = self.find_chi_sq_dof(x_l, y_l, intensity_l, gauss_min_chi)

        # a and b should not be negative since that gives a non elliptical gaussian distribution function
        for gauss, gauss_n in zip(gauss_min_chi, gauss_now):
            if gauss.a <= 0:
                gauss.a = gauss_n.a * 0.5
            if gauss.b <= 0:
                gauss.b = gauss_n.b * 0.5

        gauss_now = gauss_min_chi
        chi_sq_dof = chi

        return gauss_now, chi_sq_dof, step_min

    def initial_guess(self, peak):
        gauss_now = Gaussian()
        gauss_now.theta = 0
        gauss_now.x0 = peak[0]
        gauss_now.y0 = peak[1]
        gauss_now.amp = peak[2]
        a_nominator = peak[2]
        b_nominator = peak[2]

        """
        In certain cases some of the values next to the max point (x0, y0), can be zero. The algebraic estimate of a and
        b uses log() so input shouldn't be zero. The value of a or b is then instead set to 10000, equating to very 
        rapid decline of intensity in the direction of a or b.
        """
        gauss_now.a = 10000 if a_nominator <= 0 else -log(a_nominator / (2 * gauss_now.amp))
        gauss_now.b = 10000 if b_nominator <= 0 else -log(b_nominator / (2 * gauss_now.amp))

        return gauss_now

    def find_chi_sq_dof(self, x_l, y_l, intensity_l, gauss_now):
        """
        Finds and returns the mean squared error of the current gaussian model evaluated in every point in the image.
        """
        num_points = len(intensity_l)
        chi_sq = sum(list(map(lambda x,y,i: (i-gauss_now.get_gauss(x,y))**2, x_l, y_l, intensity_l)))

        return chi_sq / num_points

    def compute_adjustment(self, gauss_in, x_l, y_l, intensity_l):
        """
        Calculates and sets delta_gauss which contains the adjustment for gauss_now based on its partial derivatives.
        """
        num_peaks = len(gauss_in)
        delta_gauss = GaussList()
        norm_vec, norm_mat = self.make_norm_np(gauss_in, x_l, y_l, intensity_l, num_peaks)
        print(norm_mat)
        print("-------------------")
        if scipy.linalg.det(norm_mat) == 0:
            for i in range(len(norm_mat)):
                if norm_mat[i][i] < 10e-8:
                    norm_mat[i][i] = 1

        norm_inv = np.linalg.inv(norm_mat)
        adjust = np.matmul(norm_inv, norm_vec)

        for i in range(num_peaks):
            d_gauss = Gaussian()
            d_gauss.amp = adjust[0 + 6 * i]
            # Keep from making large adjustments in amplitude
            if abs(d_gauss.amp / gauss_in[i].amp) > 0.1:
                d_gauss.amp = 0.1 * gauss_in[i].amp if d_gauss.amp > 0 else -0.1 * gauss_in[i].amp
            d_gauss.a = adjust[1 + 6 * i]
            d_gauss.b = adjust[2 + 6 * i]
            d_gauss.x0 = adjust[3 + 6 * i]
            d_gauss.y0 = adjust[4 + 6 * i]
            # Keep from making large adjustments in offset
            if abs(d_gauss.x0 / max(x_l)) > 0.2:
                d_gauss.x0 = 0.2 * gauss_in[i].x0 if d_gauss.x0 > 0 else -0.2 * gauss_in[i].x0
            if abs(d_gauss.y0 / max(y_l)) > 0.2:
                d_gauss.y0 = 0.2 * gauss_in[i].y0 if d_gauss.y0 > 0 else -0.2 * gauss_in[i].y0
            d_gauss.theta = adjust[5 + 6 * i]
            delta_gauss.append(d_gauss)
        return delta_gauss

    def make_norm_np(self, gauss_in, x_l, y_l, intensity_l, num_peak):
        norm_vec = np.zeros(6 * num_peak, dtype=float)
        norm_mat = np.zeros((6 * num_peak, 6 * num_peak))
        for index, gauss in enumerate(gauss_in, 0):
            terms = list(map(lambda x,y: gauss.get_terms(x,y), x_l, y_l))
            term_a, term_b = list(list(zip(*terms))[0]), list(list(zip(*terms))[1])
            term_2, term_3 = list(list(zip(*terms))[2]), list(list(zip(*terms))[3])
            term_4, term_5 = list(list(zip(*terms))[4]), list(list(zip(*terms))[5])
            term_6 = list(list(zip(*terms))[6])

            g = list(map(lambda a,b: abs(gauss.a*a + gauss.b*b), term_a, term_b))
            g = list(map(lambda g_i: g_i if g_i<50 else 50, g))
            exp_minus_g = list(map(lambda g_i: exp(-g_i), g))

            apriori = list(map(lambda g_i: g_i*gauss.amp, exp_minus_g))
            residuals = list(map(lambda i,a: i-a, intensity_l, apriori))

            a_ta = list(map(lambda a,ta: -a*ta, apriori, term_a))
            a_tb = list(map(lambda a,tb: -a*tb, apriori, term_b))
            a_t23 = list(map(lambda a,t2,t3: a*(gauss.a*t2 + gauss.b*t3), apriori, term_2, term_3))
            a_t45 = list(map(lambda a,t4,t5: a*(gauss.a*t4 + gauss.b*t5), apriori, term_4, term_5))
            a_t6 = list(map(lambda a,t6: -a*(gauss.b - gauss.a)*t6, apriori, term_6))

            partials = [exp_minus_g, a_ta, a_tb, a_t23, a_t45, a_t6]

            for i in range(6):
                r_pi = list(map(lambda r,pi: r*pi, residuals, partials[i]))
                norm_vec[index * 6 + i] = sum(r_pi)

                for j in range(6):
                    pi_pj = list(map(lambda pi,pj: pi*pj, partials[i], partials[j]))
                    norm_mat[index * 6 + i][index * 6 + j] = sum(pi_pj)

        return norm_vec, norm_mat

def peak_local_max(x, y, intensity, threshold_abs=0.01, num_peaks=1):
    i = intensity.index(max(intensity))

    return [[x[i],y[i],intensity[i]]]