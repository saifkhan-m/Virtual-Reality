#print(self.animation_start_time,
                #self.animation_start_pos, 
                #self.animation_target_pos)
            #print("************************")
            x1=self.animation_start_pos.x
            y1=self.animation_start_pos.y

            x2=self.animation_target_pos.x
            y2=self.animation_target_pos.y

            distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)  
            pxDistance=distance*0.1*self.counter
            newX = x1
            newY = y1
            if(x1 == x2):
                newX = x1
                if(y2 > y1): 
                    newY = y1 + pxDistance
                else:
                    newY = y1 - pxDistance

            if(y1 == y2):
                newY = y1
                if(x2 > x1):
                    newX = x1 + pxDistance
                else: 
                    newX = x1 - pxDistance

            adjacent   = y2 - y1
            opposite   = x2 - x1
            hypotenuse = math.sqrt(pow(opposite, 2) + pow(adjacent,2))

            angle = math.acos(adjacent/hypotenuse)
            newOpposite = math.sin(angle) * pxDistance
            newAdjacent = math.cos(angle) * pxDistance

            newY = y1 - newAdjacent
            newX = x1 + newOpposite
            print(round(newX,3), round(newY,3))
            self.bird_node.Transform.value = self.bird_node.Transform.value * avango.gua.make_trans_mat(round(newX,3), round(newY,3), 0.0)
            
            self.counter+=1
            if abs(round(newX,3))>= abs(self.animation_target_pos.x) and abs(round(newY,3))>= abs(self.animation_target_pos.y) :
                self.animation_start_time = None
                self.animation_start_pos = None 
                self.animation_target_pos = None
                self.counter=0
