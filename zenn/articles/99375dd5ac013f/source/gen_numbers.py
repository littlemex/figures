import math
P={'H100':(0.9895e15,80,3.35),'H200':(0.9895e15,141,4.8),'B200':(2.25e15,180,8.0),'B300':(2.25e15,288,8.0)}
rp=P['B200'][0]/P['H200'][0]; rb=8.0/4.8
print('r_peak H200->B200 %.3f  r_bw %.3f  ridge H200 %.0f B200 %.0f B300 %.0f'%(rp,rb,989.5/4.8,2250/8,2250/8))
eta=0.95
def scen(name,f,r):
    S=1/sum(fi/ri for fi,ri in zip(f,r)); eff=eta*S; k=eff/rp
    g=64/eff; G=math.ceil(g); n=math.ceil(G/8)
    print('%-10s S=%.3f eff=%.3f k=%.3f gpu=%.1f->%d nodes=%.2f->%d'%(name,S,eff,k,g,G,G/8,n))
scen('allcomp',[1.0],[rp])
scen('A',[0.8,0.1,0.05,0.05],[rp,rb,1.0,1.0])
scen('B',[0.6,0.25,0.10,0.05],[rp,rb,1.0,1.0])
scen('C',[0.5,0.2,0.25,0.05],[rp,rb,1.0,1.0])
scen('C+18',[0.5,0.2,0.25,0.05],[rp,rb,1.18,1.0])
# HBM total
for n,g in [(8,'H200'),(4,'B200'),(5,'B200'),(6,'B200')]: print('HBM',n,g,n*8*P[g][1])
# implied MFU (6 N_active D only)
for nm,Na,D,h in [('Scout',17e9,40e12,5.0e6),('Maverick',17e9,22e12,2.38e6),('V3',37e9,14.8e12,2.664e6)]:
    C=6*Na*D; a=C/(h*3600); print(nm,'C=%.3g'%C,'MFU_bf16=%.1f%%'%(a/0.9895e15*100),'fp8=%.1f%%'%(a/1.979e15*100))
# pretrain example GLM-4.5-Air shape
C=6*12e9*23e12; print('C=%.3g'%C)
for m in (0.30,0.35,0.40):
    gh=C/(2.25e15*m)/3600; print('MFU',m,'GPUh %.0fK'%(gh/1e3),'days@512 %.1f'%(gh/512/24),'days@64 %.0f'%(gh/64/24))
print('1pt at 35%%: %.2f%%'%((0.35/0.34-1)*100))
# post-training shares
print('V3 post share %.2f%%'%(5/2788*100),' R1 147K/2788K %.1f%%'%(147/2788*100))
print('M1 GPUh',512*21*24,' $/h %.2f'%(534700/(512*21*24)))
print('I3 GPUh upper',512*60*24)
print('GLM-Air pretrain GPUh at 35%% H800-class %.2fM'%(C/(0.9895e15*0.35)/3600/1e6))
# KV per token bf16
kv={'GLM-4.5-Air':2*46*8*128*2,'gpt-oss-120b(full layers)':2*18*8*64*2,'DeepSeek-V3(MLA)':61*(512+64)*2,'Llama-3.1-70B':2*80*8*128*2}
for k,v in kv.items(): print('KV %-28s %7d B = %.1f KiB  32K seq = %.2f GiB'%(k,v,v/1024,v*32768/2**30))
print('gpt-oss sliding const per seq MiB %.2f'%(2*18*8*64*2*128/2**20))
# seats GLM-4.5-Air bf16 TP8 per node, 90% usable
w=106e9*2/1e9
for g in ('H200','B200','B300'):
    hbm=P[g][1]; free=(hbm*0.9-w/8)*8; seq=kv['GLM-4.5-Air']*32768/1e9
    print('seats %s free %.0f GB  seq %.2f GB  seats %d'%(g,free,seq,free//seq))
# RL FLOP share: rollout 2N/token, old-logprob 2N, train 6N
print('rollout FLOP share %.0f%%'%(2/(2+2+6)*100))
# RL scenario H200->B200
fR=[0.45,0.25,0.20,0.05,0.05]; rR=[rb,rb,1.9,1.5,1.0]
S=1/sum(a/b for a,b in zip(fR,rR)); print('RL S=%.3f eff=%.3f k=%.3f'%(S,eta*S,eta*S/rp))
# MoE decode tokens to reach ridge on B200
for nm,E,k in [('GLM-4.5-Air',128,8),('gpt-oss-120b',128,4),('DeepSeek-V3',256,8)]: print(nm,'E/k',E/k,'tokens/step for ridge B200 %.0f'%(E/k*281))
