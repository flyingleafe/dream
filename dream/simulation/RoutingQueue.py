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
Created on 11 Jul 2014

@author: Ioannis
'''
'''
Models a queue where entities can wait in order to be routed to the same server that other entities of the same parent entity have already been rooted.
if the level is reached Router object is signalled
'''


import simpy
from Queue import Queue
# ===========================================================================
#                            the Queue object
# ===========================================================================
class RoutingQueue(Queue):
    #===========================================================================
    # the __init__ method of the Queue
    #===========================================================================
    def __init__(self, id, name, capacity=1, isDummy=False, schedulingRule="FIFO", gatherWipStat=False,level=None):
        Queue.__init__(self, id, name,capacity,isDummy,schedulingRule,gatherWipStat)
        if level:
            assert level<=self.capacity, "the level cannot be bigger than the capacity of the queue"
        self.level=level
    
    # =======================================================================
    #    checks if the Queue can dispose an entity to the following object
    #            it checks also who called it and returns TRUE 
    #           only to the receiver that will give the entity. 
    #              this is kind of slow I think got to check   
    # TODO: check which route the entities of the same parent entity have picked and route them the same way
    # =======================================================================
    def haveToDispose(self, callerObject=None): 
        activeObjectQueue=self.Res.users     
        #if we have only one possible receiver just check if the Queue holds one or more entities
        if(callerObject==None):
            return len(activeObjectQueue)>0 
        thecaller=callerObject
        # local flag to control whether the callerObject can receive any of the entities in the buffers internal queue 
        isInRouting=False
        # for each entity in the buffer
        for entity in activeObjectQueue:
            # if the receiver is None then they can proceed
            if not entity.receiver:
                isInRouting=True
                break
            # otherwise check if the calleObject is the receiver of the entity
            elif thecaller==entity.receiver:
                # if yes then that entity can proceed
                isInRouting=True
                break
        return len(activeObjectQueue)>0 and (thecaller in self.next) and isInRouting
    
    #===========================================================================
    # sort the entities of the queue for the receiver
    # TODO should a sortEntitiesForReceiver method to bring to the front the entity that can proceed in that route
    #===========================================================================
    def sortEntitiesForReceiver(self, receiver=None):
        activeObjectQueue=self.getActiveObjectQueue()
        # find the entities that have None as receiver and update their receiver to the receiver provided as argument to the method
        #     the entities that have no receiver can proceed as none of their siblings have gone through the next of the activeObject
        for entity in activeObjectQueue:
            if not entity.receiver:
                entity.receiver=receiver
        activeObjectQueue.sort(key=lambda x: x.receiver==receiver, reverse=True)
    
    # =======================================================================
    #                    removes an entity from the Object
    # =======================================================================
    def removeEntity(self, entity=None):
        activeEntity=Queue.removeEntity(self, entity)                  #run the default method
        # check if the queue is empty, if yes then try to signal the router, operators may need reallocation
        if self.level:
            if not len(self.getActiveObjectQueue()):
                from Globals import G
                if not G.Router.invoked:
                    G.Router.invoked=True
                    G.Router.isCalled.succeed(G.env.now)
        return activeEntity
    
    # =======================================================================
    #            gets an entity from the predecessor that 
    #                the predecessor index points to
    # =======================================================================     
    def getEntity(self):
        activeEntity=Queue.getEntity(self)  #run the default behavior
        # update the receiver object of the entity just received according to the routing of the parent batch
        activeEntity.receiver=None
        try:
            for nextObj in self.next:
                if nextObj in entity.parentBatch.routing():
                    entity.receiver=nextObj
                    break
        # if none of the siblings (same parentBatch) has gone through the buffer then the receiver should remain None 
        except:
            pass
        # if the level is reached then try to signal the Router to reallocate the operators
        if self.level:
            if len(self.getActiveObjectQueue())==self.level:
                from Globals import G
                if not G.Router.invoked:
                    G.Router.invoked=True
                    G.Router.isCalled.succeed(G.env.now)
        return activeEntity
    
    # =======================================================================
    #    sorts the Entities of the Queue according to the scheduling rule
    # TODO: sort the entities according to the schedulingRUle and then sort them again 
    #     bringing to the front the entities that can proceed
    # =======================================================================
    def sortEntities(self):
        #if we have sorting according to multiple criteria we have to call the sorter many times
        if self.schedulingRule=="MC":
            for criterion in reversed(self.multipleCriterionList):
               self.activeQSorter(criterion=criterion) 
        #else we just use the default scheduling rule
        else:
            self.activeQSorter()
        # sort again according to the existence or not of receiver attribute of the entities
        activeObjectQueue=self.getActiveObjectQueue()
        activeObjectQueue.sort(key=lambda x: x.receiver, reverse=True)
