import  numpy as np
from scipy import optimize

class trainer(object):
    def __init__(self,NN):
        self.N=NN

    def cost_func(self,parameters,x,y):
        self.N.set_parameters(parameters)
        cost=self.N.total_err(x,y)
        gradient=self.N.weight_gradient(x,y)
        return cost,gradient

    def train(self,x,y):
        self.x=x
        self.y=y
        parameters0=self.N.get_parameters()
        res=optimize.minimize(self.cost_func,x0=parameters0,jac=True, \
                              args=(x,y),method="BFGS",options={"maxiter":200,"disp":True})
        self.N.set_parameters(res.x)
        print res.x

class neural_network(object):
    def __init__(self, hidden_layer=3,output_layer=1):

        self.input_layer=2
        self.hidden_layer=3
        self.output_layer=1
        self.w1=np.random.randn(self.input_layer,self.hidden_layer)
        self.w2=np.random.randn(self.hidden_layer,self.output_layer)

    def forward_prop(self,x):
        self.z2=np.dot(x,self.w1)
        self.a2=self.sigmoid(self.z2)
        self.z3=np.dot(self.a2,self.w2)
        y_hat=self.sigmoid(self.z3)
        return y_hat

    def weight_gradient(self,x,y):
        # gradient with respect to w2
        yhat=self.forward_prop(x)
        sigma3=-1*(y-yhat)*self.sigmoid_prime(self.z3)
        w2gradient=np.dot(np.transpose(self.a2),sigma3)


        w1gradient=np.dot(sigma3,np.transpose(self.w2))
        w1gradient*=self.sigmoid_prime(self.z2)
        w1gradient=np.dot(np.transpose(x),w1gradient)

        return np.concatenate((w1gradient.ravel(),w2gradient.ravel()))


        #gradient with respect to w1

    def sigmoid_prime(self,x):
        return np.exp(x)/(1+np.exp(x))**2

    def total_err(self,x,y):
        yhat=self.forward_prop(x)
        return 0.5 * sum((y -yhat) ** 2)

    def sigmoid(self,x):
        return 1/(1+np.exp(-x))

    def get_parameters(self):
        return np.concatenate((self.w1.ravel(),self.w2.ravel()))

    def set_parameters(self,parameters):
        w1_start=0
        w1_end=self.input_layer*self.hidden_layer
        w2_end=w1_end+self.hidden_layer*self.output_layer
        self.w1=np.reshape(parameters[w1_start:w1_end],(self.input_layer,self.hidden_layer))
        self.w2=np.reshape(parameters[w1_end:w2_end],(self.hidden_layer,self.output_layer))





x=np.reshape([3.,5.,5.,1.,10.,2.],(3,2))
x=x/np.amax(x,axis=0)
y=np.reshape([75.,82.,93.],(3,1))
y/=100
NN=neural_network()
TR=trainer(NN)
TR.train(x,y)
print NN.forward_prop([25 ,29])

