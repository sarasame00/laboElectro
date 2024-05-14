elecmodel = createpde("electromagnetic","electrostatic");

x1 = [108, 112, 112, 108];
y1 = [50, 50, 150, 150];
x2 = [168, 172, 172, 168];
y2 = [50, 50, 150, 150];
x3 = [0 ,280, 280, 0];
y3 = [0, 0, 200, 200];

p1 = [2 4 x1 y1];
p2 = [2 4 x2 y2];
p3 = [2 4 x3 y3];
gd = [p1' p2' p3'];

d = decsg(gd,'P3-P1-P2',char('P1','P2','P3')');

geometryFromEdges(elecmodel,d);

elecmodel.VacuumPermittivity = 8.8541878128E-12;
electromagneticProperties(elecmodel,"RelativePermittivity",1.2); 

electromagneticBC(elecmodel,"Voltage", 10, "Edge",[6, 9, 10, 7]);
electromagneticBC(elecmodel,"Voltage", 0, "Edge",[1, 11, 12, 8]);

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
