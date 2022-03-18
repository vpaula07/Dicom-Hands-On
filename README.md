# Handling Series

![Handling Series](img/handling_00.png)

Neste projeto, vamos nos concentrar em entender como lidar com séries dicom e a hierarquia de certas tags dicom.

Alguns desses arquivos dicom fazem parte de uma mesma série e, quando reunidos, formam uma imagem tridimensional de um paciente. Eles são chamados de Séries Dicom, e a série à qual um arquivo dicom específico pertence pode ser encontrada na tag dicom SeriesInstanceUID.Existe uma hierarquia de fatias, séries e estudos.

![Handling Series](img/series_00.png)

# Principais campos:

* SOPInstanceUID: Um identificador único associado a cada arquivo dicom (slice);
* SeriesInstanceUID: Um identificador exclusivo associado a cada série dicom. Várias fatias dicom podem ser associadas ao mesmo  SeriesInstanceUID (somente se a série tiver várias fatias). Em alguns casos (raios-x, por exemplo), cada série possui um único corte;
* SeriesDescription: A descrição do que uma determinada série representa;
* StudyInstanceUID: Um identificador exclusivo associado a cada estudo. Um estudo representa uma coleção de séries obtidas durante uma sessão de exame. Essa hierarquia é apresentada na figura abaixo, onde podemos ver que cada estudo pode ter uma ou mais séries, e cada paciente pode ter um ou mais estudos;
* InstanceNumber: Um número de identificação que indica uma fatia na série. Este atributo indica uma ordem das fatias, e veremos um pouco mais disso nas células a seguir;
* AccessionNumber: Semelhante ao id do estudo: representa um identificador exclusivo do estudo;
* PatientID: identificador único associado a cada paciente;
* ImagePositionPatient: Uma tupla de 3 que indica a posição do canto superior esquerdo no espaço tridimensional. A 3-tupla representa as posições nos eixos X, Y e Z.

# Conjunto de Dados

O conjunto de dados está disponível na plataforma kaggle(https://www.kaggle.com/c/rsna-str-pulmonary-embolism-detection/data).
