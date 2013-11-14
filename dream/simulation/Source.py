# ===========================================================================
# Copyright 2013 University of Limerick
#
# This file is part of DREAM.
#
# DREAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DREAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DREAM.  If not, see <http://www.gnu.org/licenses/>.
# ===========================================================================
'''
Created on 8 Nov 2012

@author: George
'''

'''
models the source object that generates the entities
'''

from SimPy.Simulation import now, Process, Resource, infinity, hold
from Part import Part
from RandomNumberGenerator import RandomNumberGenerator
from CoreObject import CoreObject
from Globals import G
#============================================================================
#                 The Source object is a Process
#============================================================================
class Source(CoreObject): 
    def __init__(self, id, name, distribution='Fixed', mean=1, item=Part):
        Process.__init__(self)
        # general properties
        self.id=id   
        self.objName=name   
        self.distType=distribution                      # label that sets the distribution type
        # properties used for statistics
        self.totalInterArrivalTime=0                    # the total interarrival time 
        self.numberOfArrivals=0                         # the number of entities that were created
        # list containing objects that follow in the routing 
        self.next=[]                                    # list with the next objects in the flow
        self.nextIds=[]                                 # list with the ids of the next objects in the flow
        self.previousIds=[]                             # list with the ids of the previous objects in the flow. 
                                                        # For the source it is always empty!
        self.type="Source"                              #String that shows the type of object
        self.rng=RandomNumberGenerator(self, self.distType)
        self.rng.avg=mean
        self.item=item                                  #the type of object that the Source will generate
        
    def initialize(self):
        # using the Process __init__ and not the CoreObject __init__
        CoreObject.initialize(self)
#         Process.__init__(self) 
#         # no predecessor or successor index
        
#         self.Up=True                    #Boolean that shows if the object is in failure ("Down") or not ("up")
#         self.currentEntity=None      
#         # ============================== total times ===============================================
#         self.totalBlockageTime=0                                #holds the total blockage time
#         self.totalFailureTime=0                                 #holds the total failure time
#         self.totalWaitingTime=0                                 #holds the total waiting time
#         self.totalWorkingTime=0                                 #holds the total working time
#         self.completedJobs=0                                    #holds the number of completed jobs 
#         # ============================== Entity related attributes =================================
#         self.timeLastEntityEnded=0                              #holds the last time that an entity 
#                                                                  # ended processing in the object
#         self.nameLastEntityEnded=""                             #holds the name of the last entity 
#                                                                  #that ended processing in the object
#         self.timeLastEntityEntered=0                            #holds the last time that an 
#                                                                  #entity entered in the object
#         self.nameLastEntityEntered=""                           #holds the name of the last 
#                                                                  #entity that entered in the object
#         self.timeLastFailure=0                                  #holds the time that the last 
#                                                                  #failure of the object started
#         self.timeLastFailureEnded=0                             #holds the time that the last 
#                                                                  #failure of the object Ended
#         # ============================== failure related times =====================================
#         self.downTimeProcessingCurrentEntity=0                  #holds the time that the object was down 
#                                                                  #while processing the current entity
#         self.downTimeInTryingToReleaseCurrentEntity=0           #holds the time that the object was down while trying 
#                                                                  #to release the current entity  
#         self.downTimeInCurrentEntity=0                          #holds the total time that the object was down 
#                                                                  #while holding current entity
#         self.timeLastEntityLeft=0                               #holds the last time that an entity left the object
#                                                 
#         self.processingTimeOfCurrentEntity=0        #holds the total processing time that the current entity required                                               
#         # ============================== waiting flag ==============================================
#         self.waitToDispose=False    #shows if the object waits to dispose an entity  
         
        # initialize the internal Queue (type Resource) of the Source 
        self.Res=Resource(capacity=infinity)
        self.Res.activeQ=[]                                 
        self.Res.waitQ=[]                                   
        
    def run(self):
        # get active object and its queue
        activeObject=self.getActiveObject()
        activeObjectQueue=self.getActiveObjectQueue()
        
        while 1:
            entity=self.createEntity()                            # create the Entity object and assign its name 
            entity.creationTime=now()                             # assign the current simulation time as the Entity's creation time 
            entity.startTime=now()                                # assign the current simulation time as the Entity's start time 
            entity.currentStation=self                            # update the current station of the Entity
            G.EntityList.append(entity)
            self.outputTrace(entity.name, "generated")          # output the trace
            activeObjectQueue.append(entity)                      # append the entity to the resource 
            self.numberOfArrivals+=1                              # we have one new arrival
            G.numberOfEntities+=1       
            yield hold,self,self.calculateInterarrivalTime()      # wait until the next arrival
    #============================================================================
    #            sets the routing out element for the Source
    #============================================================================
    def defineRouting(self, successorList=[]):
        self.next=successorList                                   # only successors allowed for the source
    #============================================================================        
    #                          creates an Entity
    #============================================================================
    def createEntity(self):
        return self.item(id = self.item.type+str(G.numberOfEntities), name = self.item.type+str(self.numberOfArrivals)) #return the newly created Entity
    #============================================================================
    #                    calculates the processing time
    #============================================================================
    def calculateInterarrivalTime(self):
        return self.rng.generateNumber()    #this is if we have a default interarrival  time for all the entities
    #============================================================================
    #                  outputs message to the trace.xls. 
    #          Format is (Simulation Time | Entity Name | "generated")
    #============================================================================   
