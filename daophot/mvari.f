       SUBROUTINE mvari(VX,VZ,NP,nc,par,wei,beta,FS,pes,lfl)
C
C       fit con integrale sul pixel
C	FIT CON nc curve di Moffat MONODIMENSIONALI (nc max = ng)
C	lfl=0   3 parametri variabili + fondo
c       lfl=1   3 parametri variabili (fondo fisso)
c       lfl=2   2 parametri variabili + fondo (posizioni fisse)
c       lfl=3   2 parametri variabili (fondo e posizioni fissi)
c       lfl=4   2 parametri variabili + fondo (sigma fissi)
c       lfl=5   2 parametri variabili (fondo e sigma fissi)
c       lfl=6   variabili solo altezza e fondo
c       lfl=7   varia solo l'altezza
C
        parameter (ng=20 , nv=ng*3+1)
        DIMENSION VX(*),VZ(*),par(*),pes(*),wei(*) 
        DIMENSION RMT(nv,nv),VTN(nv),VFZ(nv),VFF(nv),VC(nv),fk(ng)
        DIMENSION HE(3),HX(3)
        DATA HX/-.774597,0.,.774597/
        DATA HE/.555555,.888889,.555555/
        kc=3
        if(lfl.gt.1) kc=2
        if(lfl.gt.5) kc=1
        kfo=1-(lfl-lfl/2*2)
        nin=nc*kc+kfo
        DO I=1,nin
          VFF(I)=0
          VFZ(I)=0
          VC(I)=0
          vtn(i)=0
          DO J=1,nin
            RMT(I,J)=0
          END DO
        END DO
        do i=1,nc
          FK(i)=1./(par(i*3+1)**2)
        end do
        betar=-beta-1
        vpi=par(1)
        vtn(1)=1
        DO K=1,NP
          fno=0
          do l=1,nc
            n=l*kc
            n2=l*3
            do i=1,3
              xt=0.5*hx(i)+vx(k)
              hh=he(i)
              EPES=(Xt-par(n2))**2
              epe=1.+epes*fk(l)
              EP=epe**(-beta)
              ep2=epe**(betar)
              CO=par(n2-1)*beta*EP2*2.*FK(l)
              due=hh*CO*(Xt-par(n2))
              tre=hh*co*epes/par(n2+1)
              FNO=fno+par(n2-1)*EP*hh
              if(lfl.eq.0) then
                VTN(n-1)=VTN(n-1)+hh*EP
                VTN(n)=VTN(n)+due
                VTN(n+1)=VTN(n+1)+tre
              else if(lfl.eq.1) then
                vtn(n-2)=VTN(n-2)+ep*hh
                VTN(n-1)=VTN(n-1)+due
                VTN(n)=VTN(n)+tre
              else if(lfl.eq.2) then
                vtn(n)=VTN(n)+ep*hh
                vtn(n+1)=VTN(n+1)+tre
              else if(lfl.eq.3) then
                vtn(n-1)=VTN(n-1)+ep*hh
                vtn(n)=VTN(n)+tre
              else if(lfl.eq.4) then
                vtn(n)=VTN(n)+ep*hh
                vtn(n+1)=VTN(n+1)+due
              else if(lfl.eq.5) then
                vtn(n-1)=VTN(n-1)+ep*hh
                vtn(n)=VTN(n)+due
              else if(lfl.ge.6) then
                vtn(n+kfo)=VTN(n+kfo)+ep*hh
              end if
            END DO
          END DO
          fno=fno/2+vpi
          do i=1,nin
            vtn(i)=vtn(i)/2
          end do
          DO I=1,nin
            VFZ(I)=VFZ(I)+VZ(K)*VTN(I)*wei(k)
            VFF(I)=VFF(I)+FNO*VTN(I)*wei(k)
            DO J=1,nin
              RMT(I,J)=RMT(I,J)+VTN(I)*VTN(J)*wei(k)
            END DO
          END DO
        END DO
       DO I=1,nin
         RMT(I,I)=RMT(I,I)*(1+FS**2)
         VC(I)=VC(I)+VFZ(I)-VFF(I)
       END DO
       Nd=nv
       CALL LISI2(RMT,VC,nin,Nd)
       if(kfo.eq.1) par(1)=vc(1)*pes(1)+par(1)
       DO i=1,nc
         do k=1+kfo,kc+kfo
           in=k+kc*(i-1)
           inp=k+3*(i-1)
           kd=k-k/2*2
           kd2=1-kd
           if(lfl.eq.0) then
             par(in)=VC(in)*pes(k)+par(in)
           else if(lfl.eq.1) then
             par(in+1)=VC(in)*pes(k+1)+par(in+1)
           else if(lfl.eq.2) then
             par(inp+kd)=VC(in)*pes(k+kd)+par(inp+kd)
           else if(lfl.eq.3) then
             par(inp+1+kd2)=VC(in)*pes(k+1+kd2)+par(inp+1+kd2)
           else if(lfl.eq.4) then
             par(inp)=VC(in)*pes(k)+par(inp)
           else if(lfl.eq.5) then
             par(inp+1)=VC(in)*pes(k+1)+par(inp+1)
           else if(lfl.eq.6) then
             par(inp)=VC(in)*pes(2)+par(inp)
           else if(lfl.eq.7) then
             par(inp+1)=VC(in)*pes(2)+par(inp+1)
           end if
         end do
       END DO
       RETURN
       END
