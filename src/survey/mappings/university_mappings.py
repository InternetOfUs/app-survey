from __future__ import absolute_import, annotations

from typing import Dict

UNIV_LSE_DEPARTMENT_MAPPING = {
    "LSEDEP01": "Department of Accounting",
    "LSEDEP02": "Department of Anthropology",
    "LSEDEP03": "Department of Economics",
    "LSEDEP04": "Department of Economic History",
    "LSEDEP05": "European Institute",
    "LSEDEP06": "Department of Finance",
    "LSEDEP07": "Department of Gender Studies",
    "LSEDEP08": "Department of Geography and Environment",
    "LSEDEP09": "Institute of Global Affairs (IGA)",
    "LSEDEP10": "Department of Government",
    "LSEDEP11": "Department of Health Policy",
    "LSEDEP12": "Department of International Development",
    "LSEDEP13": "Department of International History",
    "LSEDEP14": "International Inequalities Institute",
    "LSEDEP15": "Department of International Relations",
    "LSEDEP16": "Language Centre",
    "LSEDEP17": "Department of Law",
    "LSEDEP18": "Department of Management",
    "LSEDEP19": "Marshall Institute",
    "LSEDEP20": "Department of Mathematics",
    "LSEDEP21": "Department of Media and Communications",
    "LSEDEP22": "Department of Methodology",
    "LSEDEP23": "Department of Philosophy, Logic and Scientific Method",
    "LSEDEP24": "Department of Psychological and Behavioural Science",
    "LSEDEP25": "School of Public Policy (formerly Institute of Public Affairs)",
    "LSEDEP26": "Department of Social Policy",
    "LSEDEP27": "Department of Sociology",
    "LSEDEP28": "Department of Statistics"
}

UNIV_LSE_DEGREE_MAPPING = {
    "LSEDEG01": "Undergraduate year 1",
    "LSEDEG02": "Undergraduate year 2",
    "LSEDEG03": "Undergraduate year 3",
    "LSEDEG04": "Undergraduate year 4",
    "LSEDEG05": "MSc/MA",
    "LSEDEG06": "MPhil/MRes/PhD"
}
UNIV_AAU_DEPARTMENT_MAPPING = {
    "AAUDEP01": "City, Dwelling And Settlement (BBB), MSc",
    "AAUDEP02": "Communication (KOM), MA",
    "AAUDEP03": "Communication And Digital Media (KDM), BA",
    "AAUDEP04": "Computer Engineering (CCT), BSc",
    "AAUDEP05": "Construction Management And Informatics (LIB), MSc",
    "AAUDEP06": "Cyber-Security (CS), MSc",
    "AAUDEP07": "Global Refugee Studies - Development and International Relations (GRS), MSc",
    "AAUDEP08": "ICT, Learning and Organizational Change (ILOO), MSc",
    "AAUDEP09": "Information Studies (IS), MSc",
    "AAUDEP10": "Innovative Communication Technologies And Entrepreneurship (ICTE), MSc",
    "AAUDEP11": "Learning And Innovative Change (LFP), MA",
    "AAUDEP12": "Lighting Design (LD), MSc",
    "AAUDEP13": "Medialogy (MED), BSc",
    "AAUDEP14": "Medialogy (MED), MSc",
    "AAUDEP15": "Service Systems Design (SSD), MSc",
    "AAUDEP16": "Social Work (KSA), MSc",
    "AAUDEP17": "Sound And Music Computing (SMC), MSc",
    "AAUDEP18": "Surveying And Planning (SP), MSc",
    "AAUDEP19": "Surveying, Planning And Land Management (LAN), BSc",
    "AAUDEP20": "Surveying, Planning And Land Management (SPLM), MSc",
    "AAUDEP21": "Sustainable Biotechnology, MSc",
    "AAUDEP22": "Sustainable Cities (SusCI), MSc",
    "AAUDEP23": "Sustainable Design (BD), BSc",
    "AAUDEP24": "Sustainable Design (SD), MSc",
    "AAUDEP25": "Techno-anthropology (TAN), BSc",
    "AAUDEP26": "Techno-anthropology (TAN), MSc",
    "AAUDEP27": "Tourism (TUR), MA",
    "AAUDEP28": "Urban, Energy And Environmental Planning (BEM), BSc"
}
UNIV_AAU_DEGREE_MAPPING = {
    "AAUDEG01": "BSc/BA year 1",
    "AAUDEG02": "BSc/BA year 2",
    "AAUDEG03": "BSc/BA year 3",
    "AAUDEG04": "BSc/BA year 4 and beyond",
    "AAUDEG05": "MSc/MA year 1",
    "AAUDEG06": "MSc/MA year 2",
    "AAUDEG07": "PhD",
    "AAUDEG08": "Other"
}
UNIV_UNITN_DEPARTMENT_MAPPING = {

}
UNIV_UNITN_DEGREE_MAPPING = {

}

UNIV_NUM_DEPARTMENT_MAPPING = {
    "NUMDEP01": "Business School",
    "NUMDEP02": "School of International Relations and Public Administration",
    "NUMDEP03": "Law School",
    "NUMDEP04": "School of Applied Sciences and Engineering",
    "NUMDEP05": "School of Arts and Sciences - BRANCH OF NATURAL SCIENCES",
    "NUMDEP06": "School of Arts and Sciences - DEPARTMENT OF SOCIAL SCIENCES",
    "NUMDEP07": "School of Arts and Sciences - DEPARTMET OF HUMANITIES",
}

UNIV_NUM_DEGREE_MAPPING = {
    "NUMDEG01": "Undergraduate year 1",
    "NUMDEG02": "Undergraduate year 2",
    "NUMDEG03": "Undergraduate year 3",
    "NUMDEG04": "Undergraduate year 4",
    "NUMDEG05": "MSc/MA",
    "NUMDEG06": "PhD",
    "NUMDEG07": "Other"
}

#
UNIV_UC_DEPARTMENT_MAPPING = {

}
UNIV_UC_DEGREE_MAPPING = {

}


def get_mapping_degrees_mappings_for_university(university: str) -> Dict[str, str]:

    if university == "LSE":
        return UNIV_LSE_DEGREE_MAPPING
    elif university == "NUM":
        return UNIV_NUM_DEGREE_MAPPING
    elif university == "AAU":
        return UNIV_AAU_DEGREE_MAPPING
    else:
        raise ValueError(f"Degree Mappings for university [{university}] are not available")


def get_all_department_mapping() -> Dict[str, str]:
    result = {}
    result.update(UNIV_LSE_DEPARTMENT_MAPPING)
    result.update(UNIV_NUM_DEPARTMENT_MAPPING)
    result.update(UNIV_AAU_DEPARTMENT_MAPPING)
    result.update(UNIV_UNITN_DEPARTMENT_MAPPING)
    result.update(UNIV_UC_DEPARTMENT_MAPPING)

    return result


def get_all_degree_mapping() -> Dict[str, str]:
    result = {}
    result.update(UNIV_LSE_DEGREE_MAPPING)
    result.update(UNIV_NUM_DEGREE_MAPPING)
    result.update(UNIV_AAU_DEGREE_MAPPING)
    result.update(UNIV_UNITN_DEGREE_MAPPING)
    result.update(UNIV_UC_DEGREE_MAPPING)

    return result
