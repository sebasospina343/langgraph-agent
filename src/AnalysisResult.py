from pydantic import BaseModel
from pydantic import Field

class CedulaDeCiudadania(BaseModel):
    """A cedula de ciudadania with details."""
    full_name: str = Field(..., description="The person's full name in the cedula de ciudadania")
    id_number: str = Field(..., description="The person's id number in the cedula de ciudadania")
    date_of_birth: str = Field(..., description="The person's date of birth in the cedula de ciudadania")
    issue_date: str = Field(..., description="The person's issue date in the cedula de ciudadania")
    coincidence: bool = Field(..., description="If the person's information is the same as the API")
    coincidence_reason: str = Field(..., description="The reason why the person's information is not the same as the API")

class CertificadoLaboral(BaseModel):
    """A certificado laboral with details."""
    full_name: str = Field(..., description="The person's full name in the certificado laboral")
    salary: str = Field(..., description="The person's salary in the certificado laboral")
    coincidence: bool = Field(..., description="If the person's information is the same as the API")
    coincidence_reason: str = Field(..., description="The reason why the person's information is not the same as the API")

class ColillaDePago(BaseModel):
    """A colilla de pago with details."""
    full_name: str = Field(..., description="The person's full name in the colilla de pago")
    deductions: str = Field(..., description="The total amount of deductions from the salary")
    coincidence: bool = Field(..., description="If the person's information is the same as the API") 
    coincidence_reason: str = Field(..., description="The reason why the person's information is not the same as the API")

class AnalysisResult(BaseModel):
    """
    Structured output for the final result.
    """
    cedula_de_ciudadania: CedulaDeCiudadania = Field(..., description="The person's full name in the cedula de ciudadania")
    certificado_laboral: CertificadoLaboral = Field(..., description="The person's salary in the certificado laboral")
    colilla_de_pago_1: ColillaDePago = Field(..., description="The person's deductions in the colilla de pago")
    colilla_de_pago_2: ColillaDePago = Field(..., description="The person's deductions in the colilla de pago")
    llm_calls: int