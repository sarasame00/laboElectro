elecmodel = createpde("electromagnetic","electrostatic");

%coordenades extrems paper conductor
x = [0 ,280, 280, 0];
y = [0, 0, 200, 200];

%fons
fons = [2 4 0 280 280 0 0 0 200 200];

%fils conductors
c1 = [1 110 100 10 0 0 0 0 0 0];
c2 = [1 170 100 10 0 0 0 0 0 0];

gd = [fons' c1' c2'];

d = decsg(gd,'fons-c1-c2',char('fons','c1','c2')');

geometryFromEdges(elecmodel,d);

figure
pdegplot(elecmodel,'EdgeLabels','on','FaceLabels','on');

elecmodel.VacuumPermittivity = 8.8541878128E-12;
electromagneticProperties(elecmodel,"RelativePermittivity",1.2); 

electromagneticBC(elecmodel,"Voltage", 10, "Edge",[5, 6, 7, 8]);
electromagneticBC(elecmodel,"Voltage", 0, "Edge",[9, 10, 11, 12]);

model = generateMesh(elecmodel); 

R = solve(elecmodel); 
u = R.ElectricPotential;


figure
pdeplot(elecmodel, ...
    XYData=u, ...
    FlowData=[R.ElectricField.Ex R.ElectricField.Ey], ...
    Contour="on", ...
    Levels=20, ...
    ColorMap="turbo")

axis([0 280 0 200])
set(gca,'DataAspectRatio',[1 1 1])
