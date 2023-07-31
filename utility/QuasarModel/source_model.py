import numpy as np
from numpy import log, where, amax, exp
from skimage.feature import peak_local_max
from utility.QuasarModel.gauss import Gaussian, GaussList
import copy
import scipy


class SourceModel:
    stop: bool = False

    def process(self, image):
        """
        Model a quasar image with gaussian functions.
        :param image: np.array of image data
        :return: org - original input image, mdl - modelled image, anl - analytical fourier transform of modelled image
        """

        size = image.shape[0]
        org = copy.deepcopy(image)

        gauss_fnd = GaussList(size=size)

        for guess in range(10):
            if self.stop:
                break

            peaks_position = peak_local_max(image, min_distance=3, threshold_abs=amax(org)*0.1,
                                            exclude_border=True, num_peaks=10)
            num_peaks = len(peaks_position)
            if num_peaks == 0:
                break

            gauss_now = GaussList(size=size)

            for i in range(num_peaks):
                gauss_now.append(self.initial_guess(peaks_position[i][0], peaks_position[i][1], image))
            chi_sq_dof = self.find_chi_sq_dof(image, gauss_now)
            chi_sq_dof_old = chi_sq_dof

            gauss_now, chi_sq_dof, step_min = self.least_sq_gauss(gauss_now, image)
            delta_chi = chi_sq_dof_old - chi_sq_dof
            chi_sq_dof_old = chi_sq_dof

            for iteration in range(2, 12):
                if self.stop:
                    break

                if step_min == 0 or abs(delta_chi) < 10 ** (-8) or iteration == 11:
                    gauss_fnd.append(gauss_now)
                    image_comp = gauss_fnd.build_image()
                    image = image - image_comp
                    break
                else:
                    gauss_now, chi_sq_dof, step_min = self.least_sq_gauss(gauss_now, image)
                    delta_chi = chi_sq_dof_old - chi_sq_dof
                    chi_sq_dof_old = chi_sq_dof

        mdl = gauss_fnd.build_image()

        anl = abs(sum([np.fromfunction(lambda x, y: gauss.get_fourier_transform_value(x, y, size),
                                       (size, size), dtype=float) for gauss in gauss_fnd]))

        return org, mdl, anl, gauss_fnd

    def least_sq_gauss(self, gauss_now, image):

        delta_gauss = self.compute_adjustment(gauss_now, image)
        chi_from_step = []
        steps = [0, 0.6, 1.2]  # Three points which a parabola is fitted through

        for step in steps:
            chi_from_step.append(self.find_chi_sq_dof(image, gauss_now.add(delta_gauss, step)))

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
        chi = self.find_chi_sq_dof(image, gauss_min_chi)

        # a and b should not be negative since that gives a non elliptical gaussian distribution function
        for gauss, gauss_n in zip(gauss_min_chi, gauss_now):
            if gauss.a <= 0:
                gauss.a = gauss_n.a * 0.5
            if gauss.b <= 0:
                gauss.b = gauss_n.b * 0.5

        gauss_now = gauss_min_chi
        chi_sq_dof = chi

        return gauss_now, chi_sq_dof, step_min

    def initial_guess(self, x0, y0, image):
        gauss_now = Gaussian()
        gauss_now.theta = 0
        gauss_now.amp = image[x0][y0]
        gauss_now.x0 = where(image == gauss_now.amp)[0][0]
        gauss_now.y0 = where(image == gauss_now.amp)[1][0]
        a_nominator = image[gauss_now.x0 + 1][gauss_now.y0] + image[gauss_now.x0 - 1][gauss_now.y0]
        b_nominator = image[gauss_now.x0][gauss_now.y0 + 1] + image[gauss_now.x0][gauss_now.y0 - 1]

        """
        In certain cases some of the values next to the max point (x0, y0), can be zero. The algebraic estimate of a and
        b uses log() so input shouldn't be zero. The value of a or b is then instead set to 10000, equating to very 
        rapid decline of intensity in the direction of a or b.
        """
        gauss_now.a = 10000 if a_nominator <= 0 else -log(a_nominator / (2 * gauss_now.amp))
        gauss_now.b = 10000 if b_nominator <= 0 else -log(b_nominator / (2 * gauss_now.amp))

        return gauss_now

    def find_chi_sq_dof(self, image_data, gauss_now):
        """
        Finds and returns the mean squared error of the current gaussian model evaluated in every point in the image.
        """
        full_size = image_data.shape[0]
        num_points = full_size * full_size
        mdl_data = gauss_now.build_image()
        chi_sq = np.sum(np.sum(np.power((np.subtract(image_data, mdl_data)), 2)))

        return chi_sq / num_points

    def compute_adjustment(self, gauss_in, image):
        """
        Calculates and sets delta_gauss which contains the adjustment for gauss_now based on its partial derivatives.
        """
        size = image.shape[0]
        num_peaks = len(gauss_in)
        delta_gauss = GaussList(size=size)
        norm_vec, norm_mat = self.make_norm_np(gauss_in, image, num_peaks)

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
            if abs(d_gauss.x0 / image.shape[0]) > 0.2:
                d_gauss.x0 = 0.2 * gauss_in[i].x0 if d_gauss.x0 > 0 else -0.2 * gauss_in[i].x0
            if abs(d_gauss.y0 / image.shape[0]) > 0.2:
                d_gauss.y0 = 0.2 * gauss_in[i].y0 if d_gauss.y0 > 0 else -0.2 * gauss_in[i].y0
            d_gauss.theta = adjust[5 + 6 * i]
            delta_gauss.append(d_gauss)
        return delta_gauss

    def make_norm_np(self, gauss_in, image, num_peak):
        norm_vec = np.zeros(6 * num_peak, dtype=float)
        norm_mat = np.zeros((6 * num_peak, 6 * num_peak))
        for index, gauss in enumerate(gauss_in, 0):
            terms = np.fromfunction(gauss.get_terms, (image.shape[0], image.shape[0]), dtype=float)
            term_a, term_b = terms[::][0], terms[::][1]
            g = abs(gauss.a * term_a + gauss.b * term_b)
            g[g > 50.] = 50.
            exp_minus_g = exp(-g)

            apriori = exp_minus_g * gauss.amp
            residuals = image - apriori
            partials = [exp_minus_g,
                        -apriori * term_a,
                        -apriori * term_b,
                        apriori * (gauss.a * terms[::][2] + gauss.b * terms[::][3]),
                        apriori * (gauss.a * terms[::][4] + gauss.b * terms[::][5]),
                        -apriori * (gauss.b - gauss.a) * terms[::][6]
                        ]

            for i in range(6):
                norm_vec[index * 6 + i] = np.sum(residuals * partials[i])
                for j in range(6):
                    norm_mat[index * 6 + i][index * 6 + j] = np.sum(partials[i] * partials[j])

        return norm_vec, norm_mat