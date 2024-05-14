elecmodel = createpde("electromagnetic","electrostatic");

%fons
fons = [2 4 0 280 280 0 0 0 200 200];

%triangles exteriors
t1 = [2 3 70 210 140 40 40 160 0 0];
t2 = [2 3 77 203 140 44 44 153 0 0];

%triangles interiors
t3 = [2 3 115 165 140 93 93 50 0 0];
t4 = [2 3 120 160 140 90 90 55 0 0];
gd = [fons' t1' t2' t3' t4'];

d = decsg(gd,'fons-(t1-t2)-(t3-t4)',char('fons','t1','t2','t3','t4')');

geometryFromEdges(elecmodel,d);

figure
pdegplot(elecmodel,'EdgeLabels','on','FaceLabels','on');

elecmodel.VacuumPermittivity = 8.8541878128E-12;
electromagneticProperties(elecmodel,"RelativePermittivity",1.2); 

electromagneticBC(elecmodel,"Voltage", 10, "Edge",[3, 4, 14, 15, 10, 11]);
electromagneticBC(elecmodel,"Voltage", 0, "Edge",[13, 12, 5, 6, 16, 7]);

model = generateMesh(elecmodel); 

R = solve(elecmodel); 
u = R.ElectricPotential;


figure
pdeplot(elecmodel, ...
    XYData = u, ...
    FlowData = [R.ElectricField.Ex R.ElectricField.Ey], ...
    Contour = "on", ...
    Levels = 10, ...
    ColorMap = "turbo")
axis([0 280 0 200])
set(gca,'DataAspectRatio',[1 1 1])
