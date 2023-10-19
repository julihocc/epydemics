

## Introduction

Lets consider the following SIRD Model
$$
S'(t) = - \alpha(t) \frac{S(t)I(t)}{S(t)+I(t)} \\
I'(t) = \alpha(t) \frac{S(t)I(t)}{S(t)+I(t)} - \beta(t) I(t)  - \gamma(t) D(t) \\
 R'(t) = \beta(t) I(t) \\
D'(t) = \gamma(t) D(t)
$$
where

1. $ S(t) $ is the number of susceptible people,
2. $ I(t) $ is the number of infected,
3. $ R(t) $ is the number of recovered.
4. $ D(t) $ is the number of deceased.

Close related, we define

1. $\alpha(t)$ as the rate of infection,
2. $\beta(t)$ as the rate of recovery, and
3. $\gamma(t)$ as the rate of mortality.

Another important measure is the *basic reproduction number reproduction number:*

$R_0(t) = \frac{\alpha(t)}{\beta(t)+\gamma(t)}$

The parameter $ \alpha $ could be interpreted as the mean number of persons that a infected person has been in touch with, and $ \frac{1}{\beta} $ the mean recovery time. Most of the time, $\alpha(t)$, $\beta(t)$ and $\gamma(t)$ are considered as  constants, but these assumptions have several restrictions that are not fully compatible with the reality of COVID-19. For example, As shown in \cite[eq. 2.6]{Martcheva2015}, there is just one peak predicted by the model. Of course, this is a very simple model and we could try to add more complexity which capture many other aspect, as age or gender. For example, see \cite{Allen2008} for a complete survey on more sophisticate models.

A practical way to model the behavior of COVID-19 is using time series as in \cite{Maleki2020}, but this approach neglects the underlying mathematical models. In \cite{Andrade2021}, there is some work done attempting to find an underlying model previous to fitting  a time series for forecasting deaths, but not the one given by SIR model. In recent years methods coming from machine or deep learning have been used to find more accurate predictions using time series. For example, \cite{Singh2020} tried to use support vector machines, and \cite{Hawas2020} recurrent neural networks. However, the mathematical models are also overlooked.

However, the main problem seems to be that the classical models, as the one given above, are is too rigid to be used in the current scenario. So there is a necesity to reformulate some assumptions of the model. As shown in \cite{wacker2020time}, under certain technical assumptions, an analytical solution could be obtain  if we do not assume that the parameters in the SIR model are constant. However, there is not given a way to model these time-variable parameters.

In the present article, we shall inspect a possible and promising solution by using the above ideas, in order to model time-dependent parameters in the SIR model as time series. As we want to make this approach affordable for most people as possible, we will employ some tools from machine learning to give high accurate predictions of the pandemia. In order to illustrate this ideas, we have use data from Mexico federal goverment as given in \url{https://datos.covid-19.conacyt.mx/} at July 09, 2022.

We will analyze the following discrete generalization of the SIR model.
$$
S(t+1)-S(t) = - \alpha(t) \dfrac{S(t)I(t)}{S(t)+I(t)} \\
I(t+1)-I(t) = \alpha(t) \dfrac{S(t)I(t)}{S(t)+I(t)} - \beta(t) I(t) -\gamma(t)I(t) \\
R(t+1)-R(t) = \beta(t) I(t) \\
D(t+1)-D(t) = \gamma(T) I(t)
$$

Define $ C(t) $ as the number of confirmed cases, that is, $ C = I+R+D $. So we have 
$$
C(t+1)-C(t) =  \alpha(t) \dfrac{S(t)I(t)}{S(t)+I(t)}
$$

For the sake of simplicity, we consider a fixed total population $N$ over time, including the deceased ones.

From here, que denote the first (backward) difference $ F(t)-F(t-1) $ of a quantity $ F $ at time $ t $ as $ \Delta F(t).$

From  the discrete model above, it follows that
$$
\alpha(t) = \dfrac{S(t)+I(t)}{S(t)I(t)} \Delta C(t)\\
\beta(t) = \dfrac{\Delta R(t)}{I(t)} \\
\gamma(t) = \dfrac{\Delta D(t)}{I(t)}
$$
