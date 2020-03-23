# Assume a material object has whatever parameter
# that is specified by the model.

# A geometry object has the following vectors:
#
# L: Light source direction
# V: Observer direction
# H: Halfway vector between L and V
# N: Surface normal direction
# R: Direction that N perfectly reflects L


# Diffuse reflectivity laws
def lambert_diffuse(mat, geom):
    return mat.rho / pi

def irradiance_lambert_diffuse(mat, geom):
    return mat.rho * mat.E_0 / pi

def color_lambert_diffuse(mat, geom):
    return mat.color

phong_diffuse = lambert_diffuse

def oren_nayar_diffuse(mat, geom):
    ti = geom.theta_i
    tr = geom.theta_r
    sigma = mat.sigma
    A = 1 -0.5* sigma**2 / (sigma**2 + 0.33)
    B = 0.45 * sigma**2 / (sigma**2 + 0.09)
    alpha = max(ti, tr)
    beta = min(ti, tr)
    rho = mat.rho
    E0 = mat.E_0
    bracket = A + (B*max(0, cos(ti-tr))*sin(alpha)*cos(beta))
    return rho / pi * E0 * bracket

def minnaert_diffuse(mat, geom):
    pass

## Anisotropic
def ashikhmin_shirley_diffuse(mat, geom):
    pass

# Specular reflectivity laws

def spec_helper(mat, geom, ret_fun):
    if geom.V == geom.R: return ret_fun(mat, geom)
    else return 0

def perfect_specular(mat, geom):
    return spec_helper(mat, geom, lambda (m,g): 1)

def fresnel_perfect_specular(mat, geom):
    if geom.V == geom.R: return mat.F_0
    else return 0

def wetterer_perfect_specular(mat, geom):
    if geom.V == geom.R: return mat.F_0 / geom.mu_i
    else return 0


def lobe_helper(mat, geom, ret_fun):
    e = mat.lobe_radius
    if angle(geom.V, geom.R) < e:
        return ret_fun(mat, geom)
    else return 0

def crappy_lobe_specular(mat, geom):
    return lobe_helper(mat, geom, lambda (m,g): 1)

def lobe_specular(mat, geom):
    def ret_fun(m,g):
        return 1 / sphere_ball_area(m.lobe_radius)
    return lobe_helper(mat, geom, ret_fun)

def wetterer_lobe_specular(mat, geom):
    def ret_fun(m,g):
        return m.F_0 / sphere_ball_area(m.lobe_radius)
    return lobe_helper(mat, geom, ret_fun)


def phong_specular(mat, geom):
    return dot(geom.R, geom.V) ** mat.alpha

def blinn_phong_specular(mat, geom):
    alphaprime = 4*mat.alpha
    return dot(geom.N, geom.H) ** alphaprime

def gaussian_specular(mat, geom):
    pass

def beckmann_specular(mat, geom):
    pass

## Anisotropic
def heidrich_seidel_specular(mat, geom):
    pass

def ward_specular(mat, geom):
    pass

def cook_torrance_specular(mat, geom):
    pass

def ashikhmin_shirley_diffuse(mat, geom):
    pass


