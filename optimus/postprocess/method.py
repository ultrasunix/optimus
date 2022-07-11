from .common import PostProcess as _PostProcess
import numpy as np


class PostProcess_2D(_PostProcess):
    def __init__(self, model, verbose=False):
        super().__init__(model, verbose)
        """
        Create a PostProcess optimus object where the visualisation grid is a 2D plane.

        Parameters
        ----------
        model : an optimus model object
            optimus model object includes the solution fields on the boundaries
        verbose : boolean
            to display the log information or not
        """

    def create_computational_grid(
        self,
        resolution=[141, 141],
        plane_axes=[0, 1],
        plane_offset=0.0,
        bounding_box=[],
    ):
        """
        Create a planar grid to compute the pressure fields.

        Parameters
        ----------
        resolution : a list/tuple of two int numbers
            Number of points along each axis
        plane_axes : a list/tuple of two int numbers
            Visualisation plane. possible values are 0,1,2 for x,y,z axes, respectively
        plane_offset: float (default: 0)
            Offset the visualisation plane defined by plane_axes, along the third axis
        bounding_box: a list/tuple of four float numbers
            Bounding box specifying the visualisation section on the plane_axis: [axis1_min, axis1_max, axis2_min, axis2_max]
        """
        from .common import calculate_bounding_box, find_int_ext_points, domain_edge
        from ..utils.mesh import create_grid_points

        self.resolution = resolution
        self.plane_axes = plane_axes
        self.plane_offset = plane_offset
        if bounding_box:
            self.bounding_box = bounding_box
        else:
            self.bounding_box = calculate_bounding_box(self.domains_grids, plane_axes)
        (self.points, self.plane) = create_grid_points(
            self.resolution,
            self.plane_axes,
            self.plane_offset,
            self.bounding_box,
            mode="numpy",
        )

        (
            self.points_interior,
            self.points_exterior,
            self.index_interior,
            self.index_exterior,
        ) = find_int_ext_points(self.domains_grids, self.points, self.verbose)
        self.domains_edges = domain_edge(
            self.points_interior, self.plane_axes, alpha=0.005, only_outer=True
        )

    def compute_fields(self):
        """
        Calculate the scattered and total pressure fields in the planar grid created.
        """
        from .common import compute_pressure_fields

        (
            self.total_field,
            self.scattered_field,
            self.incident_field,
        ) = compute_pressure_fields(
            self.model,
            self.points,
            self.points_exterior,
            self.index_exterior,
            self.points_interior,
            self.index_interior,
            self.verbose,
        )

        self.l2_norm_total_field_mpa = np.linalg.norm(self.total_field)
        self.scattered_field_reshaped = np.flipud(
            self.scattered_field.reshape(self.resolution).T
        )
        self.total_field_reshaped = np.flipud(
            self.total_field.reshape(self.resolution).T
        )
        self.incident_field_reshaped = np.flipud(
            self.incident_field.reshape(self.resolution).T
        )


class PostProcess_UserDefined(_PostProcess):
    def __init__(self, model, verbose=False):
        super().__init__(model, verbose)
        """
        Create a PostProcess optimus object where the visualisation grid is user-defined points (2D/3D).

        Parameters
        ----------
        model : an optimus model object
            optimus model object includes the solution fields on the boundaries
        verbose : boolean
            to display the log information or not
        """

    def create_computational_grid(self, resolution=[], user_points=[]):
        """
        Create a planar grid to compute the pressure fields.

        Parameters
        ----------
        resolution : a list/tuple of two int numbers
            Number of points along each axis
        user_points: numpy array of size 3xN
            Points defined by a user for field calculations, points can be on a 2D plane or a 3D cloud.
        """

        import warnings
        from .common import find_int_ext_points

        try:
            self.points = user_points
            warnings.warn(
                "The user-defined points will be used for field calculations.",
                RuntimeWarning,
            )
        except ValueError:
            print("user_points must be a 3xN non-zero numpy array")

        self.resolution = resolution
        (
            self.points_interior,
            self.points_exterior,
            self.index_interior,
            self.index_exterior,
        ) = find_int_ext_points(self.domains_grids, self.points, self.verbose)

    def compute_fields(self):
        """
        Calculate the scattered and total pressure fields in the planar grid created.
        """
        from .common import compute_pressure_fields

        (
            self.total_field,
            self.scattered_field,
            self.incident_field,
        ) = compute_pressure_fields(
            self.model,
            self.points,
            self.points_exterior,
            self.index_exterior,
            self.points_interior,
            self.index_interior,
            self.verbose,
        )

        self.l2_norm_total_field_mpa = np.linalg.norm(self.total_field)
        if len(self.resolution):
            self.scattered_field_reshaped = np.flipud(
                self.scattered_field.reshape(self.resolution).T
            )
            self.total_field_reshaped = np.flipud(
                self.total_field.reshape(self.resolution).T
            )
            self.incident_field_reshaped = np.flipud(
                self.incident_field.reshape(self.resolution).T
            )


class PostProcess_3D(_PostProcess):
    def __init__(self, model, verbose=True):
        super().__init__(model, verbose)
        """
        Create a PostProcess optimus object where the visualisation grid is a union of a plan and surface meshes of the domains.

        Parameters
        ----------
        model : an optimus model object
            optimus model object includes the solution fields on the boundaries
        verbose : boolean
            to display the log information or not
        """

    def create_computational_grid(
        self,
        resolution=[141, 141],
        plane_axes=[0, 1],
        plane_offset=0.0,
        bounding_box=[],
    ):
        """
        Create a planar grid to compute the pressure fields.

        Parameters
        ----------
        resolution : a list/tuple of two int numbers
            Number of points along each axis
        plane_axes : a list/tuple of two int numbers
            Visualisation plane. possible values are 0,1,2 for x,y,z axes, respectively
        plane_offset: float (default: 0)
            Offset the visualisation plane defined by plane_axes, along the third axis
        bounding_box: a list/tuple of four float numbers
            Bounding box specifying the visualisation section on the plane_axis: [axis1_min, axis1_max, axis2_min, axis2_max]
        """

        from .common import calculate_bounding_box, find_int_ext_points
        from ..utils.mesh import create_grid_points

        self.resolution = resolution
        self.plane_axes = plane_axes
        self.plane_offset = plane_offset
        if bounding_box:
            self.bounding_box = bounding_box
        else:
            self.bounding_box = calculate_bounding_box(self.domains_grids, plane_axes)
        (self.points, self.plane) = create_grid_points(
            self.resolution,
            self.plane_axes,
            self.plane_offset,
            self.bounding_box,
            mode="gmsh",
        )

        (
            self.points_interior,
            self.points_exterior,
            self.index_interior,
            self.index_exterior,
        ) = find_int_ext_points(self.domains_grids, self.points, self.verbose)

    def compute_fields(self, file_name="planar_and_surface"):
        """
        Calculate the scattered and total pressure fields in the planar grid created.

        Parameters
        ----------
        file_name : a string
            the out file name, the results are saved as GMSH files. GMSH should be used for visualisation.
        """
        from .common import compute_pressure_fields
        import bempp.api as bempp
        import numpy as np

        (
            self.total_field,
            self.scattered_field,
            self.incident_field,
        ) = compute_pressure_fields(
            self.model,
            self.points,
            self.points_exterior,
            self.index_exterior,
            self.points_interior,
            self.index_interior,
            self.verbose,
        )

        self.l2_norm_total_field_mpa = np.linalg.norm(self.total_field)

        self.domains_grids.append(self.plane)
        grids_union_all = bempp.shapes.union(self.domains_grids)
        space_union_all = bempp.function_space(grids_union_all, "P", 1)
        domain_solutions_all = [
            self.model.solution[2 * i].coefficients
            for i in range(self.model.n_subdomains)
        ]
        domain_solutions_all.append(self.total_field)
        plot3D_ptot_all = bempp.GridFunction(
            space_union_all,
            coefficients=np.concatenate(
                [domain_solutions_all[i] for i in range(self.model.n_subdomains + 1)]
            ),
        )
        plot3D_ptot_abs_all = bempp.GridFunction(
            space_union_all,
            coefficients=np.concatenate(
                [
                    np.abs(domain_solutions_all[i])
                    for i in range(self.model.n_subdomains + 1)
                ]
            ),
        )
        bempp.export(
            file_name=file_name + "_ptot_complex.msh", grid_function=plot3D_ptot_all
        )
        bempp.export(
            file_name=file_name + "_ptot_abs.msh", grid_function=plot3D_ptot_abs_all
        )
