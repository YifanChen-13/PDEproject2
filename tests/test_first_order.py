import numpy as np
import pytest
from scipy.sparse.linalg import spsolve

from pde_bvp import Problem, assemble_core, build_grid
from pde_bvp.boundary_first_order import apply_first_order


@pytest.mark.parametrize("kind", ["neumann", "robin"])
@pytest.mark.parametrize("N", [2, 4])
def test_hand_rows_and_interior_preservation(N, kind):
    p = Problem(N, kind)
    g = build_grid(p)
    A, b = assemble_core(p, g)
    old_A, old_b = A.toarray().copy(), b.copy()
    returned_A, returned_b = apply_first_order(A, b, p, g)
    assert returned_A is A and returned_b is b
    np.testing.assert_array_equal(A.toarray()[g.interior_rows], old_A[g.interior_rows])
    np.testing.assert_array_equal(b[g.interior_rows], old_b[g.interior_rows])
    for j, row in enumerate(g.right_rows, start=1):
        expected = np.zeros(g.n_unknowns)
        expected[j * N - 2] = -N
        expected[j * N - 1] = N + (2 if kind == "robin" else 0)
        np.testing.assert_array_equal(A.getrow(row).toarray().ravel(), expected)
        assert b[row] == pytest.approx((3 if kind == "robin" else 1)*np.exp(1+j/N))
    first_A, first_b = A.toarray().copy(), b.copy()
    apply_first_order(A, b, p, g)
    np.testing.assert_array_equal(A.toarray(), first_A)
    np.testing.assert_array_equal(b, first_b)
    U = g.to_nodal(np.zeros(g.n_unknowns))
    np.testing.assert_allclose(U[[0, N], N], np.exp([1, 2]))


@pytest.mark.parametrize("kind", ["neumann", "robin"])
def test_manufactured_boundary_defect_is_first_order(kind):
    midpoint_defects = []
    for N in [8, 16, 32, 64]:
        p = Problem(N, kind)
        g = build_grid(p)
        A, b = apply_first_order(*assemble_core(p, g), p, g)
        exact = np.exp(g.X + g.Y)[1:N, 1:N+1].ravel()
        defect = (A.tocsr() @ exact - b)[g.right_rows]
        expected = np.exp(1 + g.y[1:N]) * (-np.expm1(-p.h)/p.h - 1)
        np.testing.assert_allclose(defect, expected, rtol=1e-10, atol=1e-12)
        assert np.all(defect < 0)
        midpoint_defects.append(abs(defect[N//2-1]))
    orders = np.log2(np.array(midpoint_defects[:-1])/midpoint_defects[1:])
    assert np.all((orders > 0.96) & (orders < 1.01))


@pytest.mark.parametrize("kind", ["neumann", "robin"])
def test_affine_boundary_derivative_is_exact(kind):
    p = Problem(4, kind)
    g = build_grid(p)
    A, b = apply_first_order(*assemble_core(p, g), p, g)
    # Independent probe v=2x+3y+5: v_x=2, v(1,y)=7+3y.
    v = (2*g.X + 3*g.Y + 5)[1:4, 1:5].ravel()
    expected = 2 + (2*(7 + 3*g.y[1:4]) if kind == "robin" else np.zeros(3))
    np.testing.assert_allclose((A.tocsr() @ v)[g.right_rows], expected)


def test_mismatched_grid_rejected_before_mutation():
    p = Problem(4)
    g = build_grid(p)
    A, b = assemble_core(p, g)
    with pytest.raises(ValueError):
        apply_first_order(A, b, p, build_grid(Problem(8)))
    assert A.tocsr()[g.right_rows].nnz == 0


@pytest.mark.parametrize("kind", ["neumann", "robin"])
def test_small_integrated_solve_and_boundary_error(kind):
    errors = []
    for N in [8, 16, 32]:
        p = Problem(N, kind)
        g = build_grid(p)
        A, b = apply_first_order(*assemble_core(p, g), p, g)
        A = A.tocsr()
        uh = spsolve(A, b)  # E's solver entry point remains untouched.
        U = g.to_nodal(uh)
        error = abs(U - np.exp(g.X + g.Y))
        errors.append((error.max(), error[1:N, N].max()))
        np.testing.assert_allclose(U[g.dirichlet_mask], np.exp(g.X+g.Y)[g.dirichlet_mask])
        denominator = abs(A) @ abs(uh) + abs(b)
        eta = np.max(abs(A @ uh-b)/denominator)
        assert eta < 1e-12
        assert (A-A.T).nnz > 0
    assert np.all(np.array(errors)[1:] < 0.65*np.array(errors)[:-1])
