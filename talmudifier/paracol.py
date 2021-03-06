class Paracol:
    """
    A LaTeX paracol environment, composed of boxes.
    """

    TWO_THIRDS = "0.675"
    ONE_THIRD = "0.32"
    END = "\n\n\\end{paracol}"

    @staticmethod
    def get_paracol_header(left: bool, center: bool, right: bool) -> str:
        """
        Returns a paracol header with the correct column widths.

        :param left: If true, a left column exists.
        :param center: If true, a center column exists.
        :param right: If true, a right column exists.
        """

        if left:
            if center:
                if right:
                    return r"\columnratio{" + f"{Paracol.ONE_THIRD},{Paracol.ONE_THIRD},{Paracol.ONE_THIRD}" + \
                           "}\n\\begin{paracol}{3}"
                else:
                    return r"\columnratio{0.31}" +"\n" + r"\begin{paracol}{2}"
            elif right:
                return r"\columnratio{0.5,0.5}" + "\n" + r"\begin{paracol}{2}"
            else:
                return r"\columnratio{1}\begin{paracol}{1}"
        elif right:
            if center:
                return r"\columnratio{" + Paracol.TWO_THIRDS + "}\n" + r"\begin{paracol}{2}"
            else:
                return r"\columnratio{1}" + "\n" + r"\begin{paracol}{1}"
        elif center:
            return r"\columnratio{1}" + "\n" + r"\begin{paracol}{1}"
        else:
            raise Exception("Tried defining a paracol environment for 0 columns.")

    @staticmethod
    def get_switch_from_left(left: bool, center: bool, right: bool, target: str) -> str:
        """
        Returns the switch-column command to switch from the left column to the target column.

        :param left: If true, a left column exists.
        :param center: If true, a center column exists.
        :param right: If true, a right column exists.
        :param target: The name of the target column: left, center, or right.
        """

        if target == "left":
            assert left, r"Tried to add a left column but there is none."
            return ""
        elif target == "center":
            assert center, r"Tried to add a center column but there is none."
            if left:
                return r"\switchcolumn"
            else:
                return ""
        elif target == "right":
            assert right, r"Tried to add a right column but there is none."
            if left:
                if center:
                    return r"\switchcolumn[2]"
                else:
                    return r"\switchcolumn"
            elif center:
                return r"\switchcolumn"
            else:
                return ""
        else:
            raise Exception(f"Bad column name: {target}")

    @staticmethod
    def get_column(left: bool, center: bool, right: bool, target: str, tex: str) -> str:
        """
        Returns the text of a column formatted in a paracol environment at a target column.

        :param left: If true, a left column exists.
        :param center: If true, a center column exists.
        :param right: If true, a right column exists.
        :param target: The name of the target column: left, center, or right.
        :param tex: A valid LaTeX string.
        """

        return Paracol.get_paracol_header(left, center, right) + "\n" + \
               Paracol.get_switch_from_left(left, center, right, target) + "\n" + \
               tex + "\n" + Paracol.END
