from yahoo_finance import *
from  sklearn.preprocessing import maxabs_scale
from  sklearn.preprocessing import  normalize
import matplotlib.pyplot as plt
import sqlite3 as sql
import pandas as pd
import numpy as np
from scipy import optimize
import seaborn as sns
from e import *
np.random.seed(0)
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
                              args=(x,y),method="BFGS",options={"maxiter":400,"disp":True})
        self.N.set_parameters(res.x)
        print res.x

class neural_network(object):
    def __init__(self, hidden_layer=3,output_layer=1,Lambda=0.00):

        self.input_layer=5
        self.hidden_layer=11
        self.output_layer=1
        self.Lambda=Lambda
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
        w2gradient=np.dot(np.transpose(self.a2),sigma3)+self.Lambda*self.w2


        w1gradient=np.dot(sigma3,np.transpose(self.w2))
        w1gradient*=self.sigmoid_prime(self.z2)
        w1gradient=np.dot(np.transpose(x),w1gradient)+self.Lambda*self.w1

        return np.concatenate((w1gradient.ravel(),w2gradient.ravel()))


        #gradient with respect to w1

    def sigmoid_prime(self,x):
        return (2/(np.exp(x)+np.exp(-x)))**2

    def total_err(self,x,y):
        yhat=self.forward_prop(x)
        J= 0.5 * sum((y -yhat) ** 2)+(self.Lambda/2)+0.5*self.Lambda*(np.sum(self.w1**2)+np.sum(self.w2**2))
        return J

    def sigmoid(self,x):
        return np.tanh(x)

    def get_parameters(self):
        return np.concatenate((self.w1.ravel(),self.w2.ravel()))

    def set_parameters(self,parameters):
        w1_start=0
        w1_end=self.input_layer*self.hidden_layer
        w2_end=w1_end+self.hidden_layer*self.output_layer
        self.w1=np.reshape(parameters[w1_start:w1_end],(self.input_layer,self.hidden_layer))
        self.w2=np.reshape(parameters[w1_end:w2_end],(self.hidden_layer,self.output_layer))


def evaluater(x,y):

    yobv = np.asarray(y)
    yhat = np.reshape(x,yobv.shape)
    num = np.sum((yhat - yobv) ** 2)
    den= np.var(yobv) * len(yobv)
    return num/den\






handler=Data_Handler()
# handler.data_preprocessing()
connection=sql.connect("raw_data.db")
training_input, training_output, testing_input, testing_output=handler.feed_data(.5,connection)

NN=neural_network()
TR=trainer(NN)
TR.train(training_input,training_output)


predicting_result=[]
for i in range(len(testing_input)):
    res_temp=NN.forward_prop(testing_input[i])
    predicting_result.append(res_temp)


pseudo=list(testing_output)
pseudo.pop(-1)
pseudo=list(pseudo[0])+pseudo



plt.plot(np.linspace(0,1000,len(testing_input)),predicting_result,color="red",lw=2)
# plt.plot(np.linspace(0,1000,len(testing_input)),testing_output,color="green",lw=2 )
plt.plot(np.linspace(0,1000,len(testing_input)),pseudo,color="dodgerblue",lw=3 )
plt.legend(["prediction","naive"])
sns.set_style("whitegrid")
plt.grid()
plt.show()




#evaluating the result
print "NN prediction result:", evaluater(predicting_result,testing_output)
print"Naive prediction reuslt:", evaluater(pseudo,testing_output)
print "Different between NN and naive",evaluater(pseudo[3:],predicting_result[3:])
pass
# print "traininng completed!"
